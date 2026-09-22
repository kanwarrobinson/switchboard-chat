# Switchboard Chat - Frontend

React + Tailwind CSS chat interface for the AI-powered customer support application.

## 🎯 Features

- ✅ **Modern Chat UI** - Clean, responsive design with message bubbles
- ✅ **Conversation History Sidebar** - Browse and switch between past conversations
- ✅ **Markdown Rendering** - Full markdown support with syntax-highlighted code blocks
- ✅ **Model Metadata Badges** - See which AI model answered each message
- ✅ **Query Type Indicators** - Visual distinction between FAQ and escalation queries
- ✅ **Failover Indicators** - Know when a backup provider was used
- ✅ **Real-time Typing Indicators** - "AI is thinking..." animation
- ✅ **Connection Status** - Online/offline badge
- ✅ **Session Persistence** - Conversations saved in localStorage
- ✅ **Mobile Responsive** - Works on desktop and mobile
- ✅ **Welcome Screen** - Suggested questions for new users

## 🛠️ Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **React Markdown** - Markdown rendering with GFM support
- **Prism React Renderer** - Syntax highlighting for code blocks
- **Axios** - HTTP client for API calls
- **Lucide React** - Icon library

## 📁 Project Structure

```
src/frontend/
├── src/
│   ├── components/
│   │   ├── ChatContainer.jsx       # Main chat layout
│   │   ├── Header.jsx              # Top bar with title and controls
│   │   ├── Sidebar.jsx             # Conversation history sidebar
│   │   ├── SessionList.jsx         # List of sessions
│   │   ├── SessionItem.jsx         # Individual session item
│   │   ├── MessageList.jsx         # Scrollable message feed
│   │   ├── Message.jsx             # Individual message bubble
│   │   ├── InputArea.jsx           # Text input + send button
│   │   ├── TypingIndicator.jsx    # Animated typing dots
│   │   ├── WelcomeScreen.jsx      # Initial welcome + suggestions
│   │   ├── ConnectionStatus.jsx   # Online/offline badge
│   │   └── ModelBadge.jsx         # Model/provider/query badges
│   ├── api/
│   │   └── chat.js                 # API client (axios)
│   ├── utils/
│   │   ├── storage.js              # localStorage utilities
│   │   └── generateId.js           # UUID generator
│   ├── App.jsx                     # Main app with state management
│   ├── main.jsx                    # React entry point
│   └── index.css                   # Tailwind + custom styles
├── public/
│   └── vite.svg                    # Favicon
├── index.html                      # HTML entry point
├── vite.config.js                  # Vite configuration
├── tailwind.config.js              # Tailwind configuration
├── postcss.config.js               # PostCSS configuration
├── package.json                    # Dependencies
├── Dockerfile                      # Multi-stage build (Node + nginx)
├── nginx.conf                      # nginx config for SPA
└── .gitignore
```

## 🚀 Local Development

### Prerequisites
- Node.js 20+
- npm or yarn

### Install Dependencies
```bash
cd src/frontend
npm install
```

### Run Dev Server
```bash
npm run dev
```
App will be available at `http://localhost:3000`

### Build for Production
```bash
npm run build
```
Output in `dist/` directory.

### Preview Production Build
```bash
npm run preview
```

## 🐳 Docker Build

The Dockerfile uses a multi-stage build:

1. **Builder stage** - Installs dependencies and builds React app with Vite
2. **Production stage** - Copies built files to nginx:alpine

```bash
# Build image
docker build -t frontend:local .

# Load into kind cluster
kind load docker-image frontend:local --name switchboard-chat-cluster

# Restart deployment
kubectl rollout restart deployment/frontend -n app
```

Or use the slash command:
```bash
/rebuild frontend
```

## 🌐 Deployed Access

- **Direct Service**: `frontend.app.svc.cluster.local:80`
- **Ingress**: `http://localhost/` (via nginx-ingress)

## 📡 API Integration

The frontend expects these backend endpoints:

- `POST /api/chat` - Send a message, get AI response
  - Request: `{ message: string, session_id?: string }`
  - Response: `{ session_id, response, model_used, provider, query_type }`

- `GET /api/sessions` - List all conversations (optional, for sidebar)
- `GET /api/sessions/:id` - Load specific conversation (optional)
- `GET /api/health` - Health check

## 🎨 Customization

### Change Color Theme
Edit `tailwind.config.js`:
```js
theme: {
  extend: {
    colors: {
      primary: {
        // Change these values
        500: '#0ea5e9',  // Main brand color
        600: '#0284c7',  // Hover state
        // ...
      }
    }
  }
}
```

### Toggle Metadata Visibility by Default
Edit `src/utils/storage.js`:
```js
getShowMetadata: () => {
  const value = localStorage.getItem(STORAGE_KEYS.SHOW_METADATA)
  return value === null ? false : value === 'true'  // Change true → false
}
```

### Change Suggested Questions
Edit `src/components/WelcomeScreen.jsx`:
```js
const suggestedQuestions = [
  "Your custom question 1",
  "Your custom question 2",
  // ...
]
```

## 🧪 Testing

```bash
# Lint
npm run lint

# Fix lint issues
npm run lint -- --fix
```

## 📝 Environment Variables

None required for MVP. API base URL is set to `/api` (proxied by ingress).

For advanced setups, you can use Vite's `.env` files:
```bash
# .env.local
VITE_API_BASE_URL=http://localhost:8000
```

Then in `src/api/chat.js`:
```js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
```

## 🐛 Troubleshooting

**"blank screen"**
- Check browser console for errors
- Verify `dist/` exists after build
- Check nginx logs: `kubectl logs -n app deployment/frontend`

**"API calls fail"**
- Check backend is running: `kubectl get pods -n app`
- Verify ingress routes `/api` → backend service
- Check CORS if calling from different origin

**"session not persisting"**
- localStorage might be disabled
- Check browser privacy/incognito settings

## 🔮 Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] File upload for images/documents
- [ ] Voice input
- [ ] Export conversation as PDF/text
- [ ] Dark mode toggle
- [ ] Multi-language support (i18n)
- [ ] Accessibility improvements (ARIA labels, keyboard nav)
- [ ] User authentication (if needed)
- [ ] Feedback buttons (👍/👎) on messages

## 📄 License

See root LICENSE file.
