# FROM maven:3.9-eclipse-temurin-21 AS build
# WORKDIR /app
# COPY pom.xml .
# COPY src ./src
# RUN mvn clean package -DskipTests

# FROM eclipse-temurin:21-jre
# COPY --from=build /app/target/*.jar /registry.jar
# ENTRYPOINT ["java", "-jar", "/registry.jar"]
FROM openjdk:21
COPY target/registry*.jar /registry.jar
ENTRYPOINT ["java","-jar","/registry.jar"]