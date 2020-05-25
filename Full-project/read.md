the project is about Ride-share backend development in cloud.

the user can register the name then start the ride.

description:

we have 3 instances
1. rides

2. users

3. orchestrator

the load balancer will send the request to the two instaces(user,ride) based on the request.
the data will be stored in the database.it is managed by orchestrator.
