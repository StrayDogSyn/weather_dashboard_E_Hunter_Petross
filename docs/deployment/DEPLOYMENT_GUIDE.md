# Cortana Voice Service Deployment Guide

## Production Deployment with Bot Framework

This guide demonstrates how to deploy the enhanced Cortana Voice Service in a production
environment using Microsoft Bot Framework and Azure services.

## Prerequisites

### Azure Services Required

- Azure Bot Service
- Azure Cognitive Services (Speech)
- Azure App Service or Azure Functions
- Azure Storage Account
- Azure Redis Cache (optional)
- Application Insights

### Development Tools

- Visual Studio 2022 or VS Code
- Bot Framework Emulator
- Azure CLI
- .NET 6+ SDK or Node.js 16+

## Architecture Overview

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Bot Channels  │────│  Azure Bot       │────│  App Service    │
│ (Teams, Cortana)│    │  Service         │    │  (Bot Logic)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌──────────────────┐             │
                       │  Azure Speech    │─────────────┤
                       │  Services        │             │
                       └──────────────────┘             │
                                                         │
                       ┌──────────────────┐             │
                       │  Weather API     │─────────────┤
                       │  Service         │             │
                       └──────────────────┘             │
                                                         │
                       ┌──────────────────┐             │
                       │  Azure Storage   │─────────────┘
                       │  & Redis Cache   │
                       └──────────────────┘
```

## Step 1: Azure Resource Setup

### 1.1 Create Resource Group

```bash
az group create --name "rg-cortana-weather" --location "East US"
```

### 1.2 Create Bot Service

```bash
az bot create \
  --resource-group "rg-cortana-weather" \
  --name "cortana-weather-bot" \
  --kind "webapp" \
  --sku "F0" \
  --app-type "MultiTenant"
```

### 1.3 Create Speech Service

```bash
az cognitiveservices account create \
  --name "cortana-speech-service" \
  --resource-group "rg-cortana-weather" \
  --kind "SpeechServices" \
  --sku "F0" \
  --location "East US"
```

### 1.4 Create App Service

```bash
az appservice plan create \
  --name "cortana-weather-plan" \
  --resource-group "rg-cortana-weather" \
  --sku "B1"

az webapp create \
  --name "cortana-weather-app" \
  --resource-group "rg-cortana-weather" \
  --plan "cortana-weather-plan" \
  --runtime "DOTNETCORE|6.0"
```

## Step 2: Bot Framework Implementation

### 2.1 Create Bot Project Structure

```text
cortana-weather-bot/
├── Controllers/
│   └── BotController.cs
├── Bots/
│   └── CortanaWeatherBot.cs
├── Services/
│   ├── CortanaVoiceService.cs
│   ├── WeatherService.cs
│   └── SpeechService.cs
├── Models/
│   ├── WeatherModels.cs
│   └── VoiceModels.cs
├── Dialogs/
│   ├── WeatherDialog.cs
│   └── MainDialog.cs
├── appsettings.json
└── Program.cs
```

### 2.2 Bot Controller Implementation

```csharp
// Controllers/BotController.cs
using Microsoft.AspNetCore.Mvc;
using Microsoft.Bot.Builder;
using Microsoft.Bot.Builder.Integration.AspNet.Core;

[Route("api/messages")]
[ApiController]
public class BotController : ControllerBase
{
    private readonly IBotFrameworkHttpAdapter _adapter;
    private readonly IBot _bot;

    public BotController(IBotFrameworkHttpAdapter adapter, IBot bot)
    {
        _adapter = adapter;
        _bot = bot;
    }

    [HttpPost]
    public async Task PostAsync()
    {
        await _adapter.ProcessAsync(Request, Response, _bot);
    }
}
```

### 2.3 Main Bot Implementation

```csharp
// Bots/CortanaWeatherBot.cs
using Microsoft.Bot.Builder;
using Microsoft.Bot.Schema;
using Microsoft.Extensions.Logging;

public class CortanaWeatherBot : ActivityHandler
{
    private readonly ICortanaVoiceService _cortanaService;
    private readonly ILogger<CortanaWeatherBot> _logger;
    private readonly ConversationState _conversationState;
    private readonly UserState _userState;

    public CortanaWeatherBot(
        ICortanaVoiceService cortanaService,
        ConversationState conversationState,
        UserState userState,
        ILogger<CortanaWeatherBot> logger)
    {
        _cortanaService = cortanaService;
        _conversationState = conversationState;
        _userState = userState;
        _logger = logger;
    }

    protected override async Task OnMessageActivityAsync(
        ITurnContext<IMessageActivity> turnContext, 
        CancellationToken cancellationToken)
    {
        try
        {
            var userMessage = turnContext.Activity.Text;
            _logger.LogInformation($"Processing message: {userMessage}");

            // Get conversation context
            var contextAccessor = _conversationState.CreateProperty<Dictionary<string, object>>("context");
            var context = await contextAccessor.GetAsync(turnContext, () => new Dictionary<string, object>());

            // Process with Cortana service
            var response = await _cortanaService.ProcessVoiceCommandAsync(userMessage, context);

            // Handle voice response
            var replyActivity = MessageFactory.Text(response.TextResponse);
            
            if (response.HasAudio && !string.IsNullOrEmpty(response.AudioData))
            {
                // Add speech synthesis for voice channels
                replyActivity.Speak = response.TextResponse;
                replyActivity.InputHint = InputHints.ExpectingInput;
            }

            await turnContext.SendActivityAsync(replyActivity, cancellationToken);

            // Save conversation state
            await _conversationState.SaveChangesAsync(turnContext, false, cancellationToken);
            await _userState.SaveChangesAsync(turnContext, false, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing message");
            await turnContext.SendActivityAsync(
                MessageFactory.Text("I'm sorry, I encountered an error. Please try again."),
                cancellationToken);
        }
    }

    protected override async Task OnMembersAddedAsync(
        IList<ChannelAccount> membersAdded,
        ITurnContext<IConversationUpdateActivity> turnContext,
        CancellationToken cancellationToken)
    {
        var welcomeText = "Hello! I'm Cortana, your weather assistant. Ask me about the weather in any city!";
        
        foreach (var member in membersAdded)
        {
            if (member.Id != turnContext.Activity.Recipient.Id)
            {
                var welcomeActivity = MessageFactory.Text(welcomeText);
                welcomeActivity.Speak = welcomeText;
                await turnContext.SendActivityAsync(welcomeActivity, cancellationToken);
            }
        }
    }
}
```

### 2.4 Speech Service Integration

```csharp
// Services/SpeechService.cs
using Microsoft.CognitiveServices.Speech;
using Microsoft.CognitiveServices.Speech.Audio;

public class SpeechService : ISpeechService
{
    private readonly SpeechConfig _speechConfig;
    private readonly ILogger<SpeechService> _logger;

    public SpeechService(IConfiguration configuration, ILogger<SpeechService> logger)
    {
        _speechConfig = SpeechConfig.FromSubscription(
            configuration["SpeechService:Key"],
            configuration["SpeechService:Region")
        );
        _speechConfig.SpeechSynthesisVoiceName = "en-US-JennyNeural";
        _logger = logger;
    }

    public async Task<byte[]> SynthesizeSpeechAsync(string text, VoiceSettings settings = null)
    {
        try
        {
            using var synthesizer = new SpeechSynthesizer(_speechConfig);
            
            if (settings != null)
            {
                var ssml = CreateSSML(text, settings);
                var result = await synthesizer.SpeakSsmlAsync(ssml);
                return result.AudioData;
            }
            else
            {
                var result = await synthesizer.SpeakTextAsync(text);
                return result.AudioData;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error synthesizing speech");
            return null;
        }
    }

    public async Task<string> RecognizeSpeechAsync(byte[] audioData)
    {
        try
        {
            using var audioConfig = AudioConfig.FromStreamInput(
                AudioInputStream.CreatePushStream());
            using var recognizer = new SpeechRecognizer(_speechConfig, audioConfig);
            
            var result = await recognizer.RecognizeOnceAsync();
            return result.Text;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error recognizing speech");
            return null;
        }
    }

    private string CreateSSML(string text, VoiceSettings settings)
    {
        return $@"
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
            <voice name='{settings.VoiceProfile}'>
                <prosody rate='{settings.Rate}' volume='{settings.Volume}' pitch='{settings.Pitch:+0.0;-0.0;+0.0}Hz'>
                    {text}
                </prosody>
            </voice>
        </speak>";
    }
}
```

## Step 3: Configuration

### 3.1 Application Settings

```json
{
  "MicrosoftAppType": "MultiTenant",
  "MicrosoftAppId": "",
  "MicrosoftAppPassword": "",
  "SpeechService": {
    "Key": "your-speech-service-key",
    "Region": "eastus"
  },
  "WeatherAPI": {
    "BaseUrl": "https://api.openweathermap.org/data/2.5",
    "ApiKey": "your-weather-api-key"
  },
  "Storage": {
    "ConnectionString": "your-storage-connection-string"
  },
  "Redis": {
    "ConnectionString": "your-redis-connection-string"
  },
  "ApplicationInsights": {
    "InstrumentationKey": "your-app-insights-key"
  }
}
```

### 3.2 Dependency Injection Setup

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddHttpClient();
builder.Services.AddControllers().AddNewtonsoftJson();

// Bot Framework services
builder.Services.AddSingleton<IBotFrameworkHttpAdapter, AdapterWithErrorHandler>();
builder.Services.AddSingleton<IStorage, MemoryStorage>();
builder.Services.AddSingleton<UserState>();
builder.Services.AddSingleton<ConversationState>();
builder.Services.AddTransient<IBot, CortanaWeatherBot>();

// Custom services
builder.Services.AddScoped<ICortanaVoiceService, CortanaVoiceService>();
builder.Services.AddScoped<IWeatherService, WeatherService>();
builder.Services.AddScoped<ISpeechService, SpeechService>();
builder.Services.AddScoped<ICacheService, RedisCacheService>();

// Application Insights
builder.Services.AddApplicationInsightsTelemetry();

var app = builder.Build();

// Configure pipeline
app.UseDefaultFiles();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

## Step 4: Deployment

### 4.1 Build and Package

```bash
# Build the application
dotnet build --configuration Release

# Publish for deployment
dotnet publish --configuration Release --output ./publish

# Create deployment package
zip -r cortana-weather-bot.zip ./publish/*
```

### 4.2 Deploy to Azure

```bash
# Deploy using Azure CLI
az webapp deployment source config-zip \
  --resource-group "rg-cortana-weather" \
  --name "cortana-weather-app" \
  --src "cortana-weather-bot.zip"

# Configure app settings
az webapp config appsettings set \
  --resource-group "rg-cortana-weather" \
  --name "cortana-weather-app" \
  --settings @appsettings.json
```

### 4.3 Configure Bot Channels

```bash
# Enable Cortana channel
az bot directline create \
  --resource-group "rg-cortana-weather" \
  --name "cortana-weather-bot"

# Configure messaging endpoint
az bot update \
  --resource-group "rg-cortana-weather" \
  --name "cortana-weather-bot" \
  --endpoint "https://cortana-weather-app.azurewebsites.net/api/messages"
```

## Step 5: Testing and Validation

### 5.1 Local Testing with Bot Emulator

1. Start the bot locally: `dotnet run`
2. Open Bot Framework Emulator
3. Connect to `http://localhost:3978/api/messages`
4. Test voice commands and responses

### 5.2 Production Testing

```bash
# Test bot endpoint
curl -X POST https://cortana-weather-app.azurewebsites.net/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "text": "What is the weather in Seattle?",
    "from": { "id": "test-user" },
    "channelId": "test"
  }'
```

## Step 6: Monitoring and Maintenance

### 6.1 Application Insights Queries

```kusto
// Bot conversation analytics
traces
| where timestamp > ago(24h)
| where message contains "Processing message"
| summarize count() by bin(timestamp, 1h)

// Error tracking
exceptions
| where timestamp > ago(24h)
| summarize count() by type, bin(timestamp, 1h)

// Performance metrics
requests
| where timestamp > ago(24h)
| summarize avg(duration) by bin(timestamp, 1h)
```

### 6.2 Health Checks

```csharp
// Add health checks
builder.Services.AddHealthChecks()
    .AddCheck<WeatherServiceHealthCheck>("weather-service")
    .AddCheck<SpeechServiceHealthCheck>("speech-service")
    .AddCheck<CacheServiceHealthCheck>("cache-service");

app.MapHealthChecks("/health");
```

## Security Considerations

### Authentication and Authorization

- Use Azure AD for bot authentication
- Implement rate limiting for API calls
- Validate all user inputs
- Use managed identities for Azure services

### Data Protection

- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement proper logging without exposing PII
- Follow GDPR compliance guidelines

## Performance Optimization

### Caching Strategy

- Cache weather data for 5-10 minutes
- Cache speech synthesis results
- Use Redis for distributed caching
- Implement cache warming for popular locations

### Scaling Considerations

- Use Azure App Service auto-scaling
- Implement connection pooling
- Optimize database queries
- Use CDN for static assets

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check messaging endpoint configuration
   - Verify app registration credentials
   - Review Application Insights logs

2. **Speech synthesis failures**
   - Validate Speech Service credentials
   - Check regional availability
   - Monitor quota usage

3. **Weather data issues**
   - Verify API key validity
   - Check rate limiting
   - Validate location parsing

### Diagnostic Commands

```bash
# Check bot health
az bot show --resource-group "rg-cortana-weather" --name "cortana-weather-bot"

# View app service logs
az webapp log tail --resource-group "rg-cortana-weather" --name "cortana-weather-app"

# Test speech service
az cognitiveservices account show --resource-group "rg-cortana-weather" --name "cortana-speech-service"
```

## Conclusion

This deployment guide provides a comprehensive approach to deploying the Cortana Voice Service
in a production environment using Microsoft Bot Framework and Azure services. The architecture
ensures scalability, reliability, and maintainability while providing an excellent user
experience through advanced voice capabilities.
