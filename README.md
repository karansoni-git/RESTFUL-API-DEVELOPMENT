# RESTFUL-API-DEVELOPMENT

#COMPANY: CODTECH IT SOLUTIONS
#NAME: KARAN PAREKH
#INTERN ID: CTIS1913
#DOMAIN: SOFTWARE DEVELOPMENT
#DURATION: 6 WEEEKS
#MENTOR: MUZAMMIL AHMED

DESCRIPTION : This project is a full-featured Library Management System built using Flask (Python) for the backend and a custom-designed HTML, CSS, and JavaScript interface for interactive API documentation. The system provides a RESTful API that enables efficient management of books, members, and loan transactions while maintaining clean architecture and structured responses.

The backend is developed using Flask and follows REST principles with clearly structured endpoints under /api/v1/. It supports complete CRUD operations for books, members, and loans. The API includes advanced features such as pagination, filtering (by genre, author, membership type, status), loan limits based on membership type, availability checks before issuing books, and prevention of deletion when active dependencies exist (e.g., active loans). Input validation is implemented for required fields and email format verification, and meaningful HTTP status codes are returned for both success and error scenarios.

The system uses in-memory data storage for simplicity and fast testing, but it is structured in a way that can easily be extended to integrate with SQLAlchemy or a production-level database. Utility helper functions ensure consistent JSON responses using a standardized success/error format, improving API reliability and maintainability.

On the frontend, a modern API documentation interface is built using pure HTML, CSS, and JavaScript. The UI features a dark-themed, developer-focused design with a fixed sidebar for navigation and dynamically expandable endpoint cards. Each endpoint includes method badges (GET, POST, PUT, PATCH, DELETE), request parameter tables, response examples, schema descriptions, and interactive code tabs. A copy-to-clipboard functionality allows users to quickly copy request examples, improving usability.

The JavaScript layer enhances user interaction through smooth scrolling, active link highlighting based on scroll position, collapsible endpoint sections, tab switching for code examples, and responsive sidebar behavior on mobile devices. The CSS design system uses custom variables for consistent theming, method-based color coding, and structured layout styling to create a clean and professional developer experience.

Additional API endpoints such as health checks and statistics provide system insights, including total counts of books, members, loans, and active transactions. The project demonstrates strong backend fundamentals, RESTful API design, input validation, state management, and frontend UI engineering for technical documentation.

Overall, this project showcases full-stack development capabilities by combining backend API architecture with an interactive documentation interface. It reflects best practices in API structure, error handling, user experience design, and scalable project organization, making it suitable for real-world backend service foundations.

OUTPUT : ![img](https://github.com/user-attachments/assets/4ef8a199-14bc-4947-a902-23bf3d19f27b)
