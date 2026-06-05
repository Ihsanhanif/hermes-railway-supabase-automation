# Hermes + Supabase on Railway.app

This project sets up Hermes Agent to run 24/7 on Railway.app with Supabase as the backend for persistent storage and logging.

## Features

- Hermes Agent running continuously on Railway.app
- Supabase integration for persistent storage
- Web dashboard to monitor status and logs
- Easy deployment via Railway.app GitHub integration

## Setup

### 1. Prerequisites

- [Railway.app](https://railway.app) account
- [Supabase](https://supabase.com) account
- GitHub account

### 2. Supabase Setup

1. Create a new Supabase project
2. Get your Supabase URL and anon key from Settings > API
3. Run the SQL schema in `supabase/schema.sql` to create necessary tables

### 3. Railway.app Deployment

1. Fork this repository to your GitHub account
2. Go to [Railway.app](https://railway.app) and click "New Project"
3. Select "Deploy from GitHub" and connect your forked repository
4. Railway will automatically detect the `railway.json` and start the build
5. Add the following environment variables in Railway:
   - `SUPABASE_URL` (from your Supabase project)
   - `SUPABASE_ANON_KEY` (from your Supabase project)
   - `HERMES_MODEL` (optional, defaults to your main model)
   - `HERMES_PROVIDER` (optional, defaults to your main provider)

### 4. Hermes Configuration

The Hermes configuration will be automatically generated on first run. You can customize it by:
1. Accessing the Railway shell
2. Editing `~/.hermes/config.yaml`
3. Restarting the service

## Project Structure

```
hermes-supabase-railway/
├── railway.json              # Railway configuration
├── Dockerfile               # Docker container for Hermes
├── supabase/
│   └── schema.sql           # Database schema
├── hermes/
│   ├── config.yaml          # Hermes configuration (generated)
│   └── scripts/             # Custom scripts
├── dashboard/
│   ├── index.html           # Monitoring dashboard
│   ├── script.js            # Dashboard logic
│   └── style.css            # Dashboard styling
└── start.sh                 # Startup script
```

## Monitoring Dashboard

Access the dashboard at your Railway.app URL to see:
- Hermes agent status
- Key metrics
- Recent logs

## Development

To run locally for development:

```bash
# Clone repository
git clone https://github.com/yourusername/hermes-supabase-railway.git
cd hermes-supabase-railway

# Install dependencies (if any)
# Hermes should work with its bundled dependencies

# Run Hermes locally
hermes run

# Or use Docker
docker build -t hermes-supabase .
docker run -p 8080:8080 hermes-supabase
```

## Notes

- Railway.app provides free hours that should be sufficient for 24/7 operation
- The Docker container keeps Hermes running as a background process
- All logs and metrics are stored in Supabase for persistence
- The dashboard provides a simple interface to monitor everything

## Troubleshooting

1. **Hermes not starting**: Check Railway logs for startup errors
2. **Supabase connection issues**: Verify SUPABASE_URL and SUPABASE_ANON_KEY
3. **Dashboard not loading**: Check that the dashboard files are being served correctly

## License

MIT
