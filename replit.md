# ArmonIA Vial

## Overview

ArmonIA Vial is a Flask-based educational web application promoting sustainable urban mobility in Urabá, Antioquia, Colombia. The platform focuses on road safety culture, environmental awareness, and community engagement through interactive features including educational quizzes, an interactive map, weather integration, and a virtual assistant. The application emphasizes pedagogy and modern, accessible design to educate citizens about sustainable transportation options.

## Recent Changes

**October 18, 2025**: Enhanced /comunidad section into modern Padlet-style collaborative wall:
- Redesigned community section with fresh green/blue theme (#4CAF50, #2196F3)
- Implemented AJAX-powered message posting and deletion without page reloads
- Added theme categorization (General, Cultura, Educación, Ambiente) with live filtering
- Created smooth animations (fade-in, slide-up, fade-out) for dynamic content
- Implemented XSS protection using DOM APIs instead of innerHTML
- Added proper database migration to handle schema updates
- Designed responsive card-based grid layout similar to Padlet
- Added voice counter showing total community contributions

**October 18, 2025**: Complete application implementation with all 7 sections fully functional:
- Created Flask backend with SQLite database integration
- Implemented all HTML templates with Jinja2 inheritance
- Designed modern CSS with green/blue color scheme and responsive layout
- Added JavaScript for interactive quiz and chatbot functionality
- Generated ArmonIA Vial logo
- Fixed database initialization to work with all deployment methods
- Configured workflow for automatic server startup

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Template Engine**: Jinja2 templating with a base template (`base.html`) that all pages extend, ensuring consistent navigation, header, footer, and branding across the application.

**CSS Framework**: Custom CSS with CSS variables for theming, utilizing the Poppins font family for modern typography. The design follows a card-based layout pattern with responsive grid systems.

**Animation Library**: AOS (Animate On Scroll) library for progressive content reveal and smooth user experience.

**Icon System**: Font Awesome 6.4.0 for consistent iconography throughout the interface.

**JavaScript Architecture**: Vanilla JavaScript in `main.js` handles:
- Navigation menu toggling for mobile responsiveness
- Smooth scrolling for anchor links
- Active navigation state management
- AOS initialization

**Responsive Design**: Mobile-first approach with navigation toggle functionality for smaller screens.

### Backend Architecture

**Web Framework**: Flask (Python) serving as the main application server with route-based page rendering.

**Route Structure**: Simple route handlers that render templates for different sections:
- `/` - Homepage with hero section and feature cards
- `/ambiente` - Environmental tips and sustainable mobility guidance
- `/cultura` - Road culture and behavioral principles
- `/educacion` - Interactive educational content and quizzes
- `/mapa` - Interactive map with weather integration
- `/comunidad` - Interactive Padlet-style collaborative wall with AJAX functionality
- `/api/comunidad/add` - POST endpoint for adding messages dynamically
- `/api/comunidad/delete/<id>` - DELETE endpoint for removing messages
- `/asistente` - Virtual assistant chatbot interface

**Session Management**: Flask session handling with secret key configuration from environment variables for security.

### Data Storage

**Database**: SQLite database (`armonia.db`) chosen for simplicity and portability.

**Schema Design**: Single table `mensajes` for community messages with fields:
- `id` (PRIMARY KEY, AUTOINCREMENT)
- `nombre` (TEXT, NOT NULL)
- `comentario` (TEXT, NOT NULL)
- `fecha` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)

**Database Initialization**: Automatic table creation at module import via `init_db()` function called at module level, ensuring database setup regardless of deployment method (direct Python execution or WSGI server). Includes intelligent migration logic to add `mensaje` and `tema` columns to existing databases.

**Schema Evolution**: The database schema has evolved from a simple `comentario` field to include `mensaje` (content) and `tema` (category) fields for better organization and filtering. Migration logic automatically backfills data from legacy `comentario` column.

**Connection Management**: Row factory configured to return dictionary-like Row objects for easier template integration.

### External Dependencies

**Weather API**: OpenWeatherMap API integration for displaying current weather conditions in Urabá. The application fetches weather data including temperature, description, and icon codes to display relevant mobility information (e.g., rain conditions affecting cycling).

**Mapping Service**: Leaflet.js (version 1.9.4) used for interactive map functionality, allowing visualization of:
- Safe cycling routes (ciclovías)
- School zones
- Points of interest for sustainable mobility

**CDN Resources**:
- Google Fonts (Poppins typeface)
- Font Awesome 6.4.0 (icons)
- AOS 2.3.1 (animations)
- Leaflet 1.9.4 (mapping)

**Frontend Libraries**: All major frontend dependencies loaded via CDN for simplified deployment and faster initial load times.

### Authentication & Authorization

Currently no authentication system implemented. The community message board accepts public submissions without user accounts. Future implementation may require user registration for message moderation.

### Notable Architectural Decisions

**Static Asset Organization**: Assets organized in conventional Flask structure with `/static/css/`, `/static/js/`, and `/static/images/` directories.

**Environment Configuration**: Secret key configuration supports both environment variable (`SESSION_SECRET`) and fallback development key, enabling secure production deployment.

**Bilingual Content**: All content presented in Spanish, targeting the local Colombian audience in Urabá, Antioquia.

**Progressive Enhancement**: Core content accessible without JavaScript, with AOS animations and interactive features enhancing the experience when available.

**Educational Focus**: Fully functional interactive quiz system in education section with 5 questions about sustainable mobility, real-time scoring, and educational feedback.

**Community Engagement**: Modern Padlet-style collaborative wall (`static/js/comunidad.js`) with:
- AJAX-powered real-time message posting and deletion
- Theme-based categorization and filtering (Cultura, Educación, Ambiente)
- XSS protection via secure DOM manipulation (textContent instead of innerHTML)
- Smooth animations and transitions for enhanced UX
- Toast notifications for user feedback
- Responsive card-based grid layout
- Environmental emoji icons for visual appeal