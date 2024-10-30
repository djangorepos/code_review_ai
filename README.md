# Introduction 
Auto-Review Tool is an app designed to help software developers improve
their code quality by leveraging the power of OpenAI's large language models.
The app analyzes the code in a given GitHub repository and provides
recommendations to enhance the code. It is a valuable tool for developers,
allowing them to discover potential issues in their codebase. 

# Installation process
1.	Clone repository
2.	Run docker-compose up to install all dependencies
3.	Go to your browser and use swagger endpoint, or use POSTMAN. Request body should be:
   assignment_description (string): Description of the coding assignment.
   github_repo_url (string): URL of the GitHub repository to be reviewed.
   candidate_level (string): Candidate's level, which could be "Junior," "Middle," or "Senior."
4.	Return is a structured review in this format:
   Found files
   Downsides/Comments
   Rating
   Conclusion

# Test
   Use pytest command to run all project tests

# What if
Scaling the Coding Assignment Auto-Review Tool to handle over 100 review requests per minute and large repositories presents a set of challenges that require careful architectural considerations. Below is a detailed outline of a potential system architecture along with performance considerations for scaling the tool.

1. Architectural Overview

    A. Microservices Architecture
    
    Adopting a microservices architecture will help decouple components of the system, allowing for independent scaling, development, and deployment. Key components can include:
    
    API Gateway: Handles incoming requests and routes them to appropriate microservices. It can also manage authentication and rate limiting.
    Review Service: Responsible for processing the review requests. This service can be further broken down:
    Static Analysis Service: Performs static code analysis on the submissions.
    Test Execution Service: Runs the tests defined in the coding assignments.
    Feedback Generation Service: Compiles results and generates feedback for the user.
    File Storage Service: Stores large repositories and files. Consider using a cloud storage solution for scalability.
    Queue Service: Manages incoming requests and balances the load on the Review Service. Technologies like RabbitMQ or AWS SQS can be used.
    Database Service: A scalable database (e.g., NoSQL like MongoDB or relational like PostgreSQL) for storing user data, assignment metadata, and review results.
    
    B. Event-Driven Architecture
    Incorporating an event-driven approach can enhance scalability and responsiveness:
    
    Event Bus: Use a message broker (like Kafka) for communication between microservices, ensuring asynchronous processing of tasks and decoupling of services.
    Event Sourcing: Store the state of review requests as a sequence of events, allowing easy reconstruction of the system state.

2. Handling High Throughput

   To handle over 100 review requests per minute effectively, consider the following strategies:

   A. Load Balancing

   Deploy multiple instances of the Review Service behind a load balancer to distribute incoming requests evenly. Use tools like Nginx or cloud-based load balancers.

   B. Horizontal Scaling

   Each microservice should be stateless, allowing for horizontal scaling. Increase the number of instances based on demand, using container orchestration platforms like Kubernetes.
   
   C. Caching
   
   Implement caching mechanisms (like Redis or Memcached) for frequently accessed data (e.g., user data, common review results) to reduce database load and improve response times.

3. Performance Considerations
   
   A. Repository Management

   File Chunking: For large repositories, implement file chunking to break down submissions into manageable pieces, allowing for parallel processing and reducing memory consumption.
   Asynchronous Processing: Use worker queues for handling large file reviews asynchronously, enabling the system to manage multiple requests without blocking.
   
   B. Resource Optimization
   
   Monitor and optimize resource usage (CPU, memory, I/O) to prevent bottlenecks. Use performance profiling tools to identify and address slow components.
   
   C. Auto-scaling
   
   Implement auto-scaling policies based on metrics like CPU usage, request count, and response time to automatically adjust the number of instances of microservices in real-time.

4. Security and Reliability
   
    A. Authentication and Authorization
   
    Implement secure authentication mechanisms (e.g., OAuth 2.0) for API access to protect sensitive data.
   
    B. Data Consistency
   
    Use distributed transaction management or eventual consistency models to maintain data integrity across services, especially for feedback generation and user submissions.
   
    C. Monitoring and Logging
   
    Deploy monitoring tools (like Prometheus and Grafana) to track system performance and health. Implement centralized logging (e.g., ELK stack) for error tracking and debugging.

5. Conclusion

    By adopting a microservices architecture, event-driven design, and focusing on load balancing, resource optimization, and scalability, the Coding Assignment Auto-Review Tool can efficiently handle over 100 review requests per minute and manage large repositories. Continuous monitoring and iterative improvements will be key to maintaining performance and reliability as user demands grow.
