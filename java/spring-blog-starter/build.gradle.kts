plugins {
    java
    id("org.springframework.boot") version "4.1.1"
}

repositories()
{
    mavenCentral()
}

dependencies()
{
    implementation(platform(org.springframework.boot.gradle.plugin.SpringBootPlugin.BOM_COORDINATES))
    implementation("org.springframework.boot:spring-boot-starter-webmvc")
    // The API's documentation, where you can try each route: /swagger-ui.html.
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:3.1.1")
    // For markdown fields, such as a post's body: see Site.java.
    implementation("org.commonmark:commonmark:0.30.1")
}

java()
{
    toolchain()
    {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

// The Coho values, from .env, which git ignores. A variable already set, such as
// COHO_REF=feature/x ./gradlew bootRun, wins over the same one in .env.
tasks.bootRun()
{
    val dotenv = file(".env")
    if (dotenv.exists())
    {
        environment(
            dotenv.readLines()
                .filter { '=' in it && !it.trimStart().startsWith("#") }
                .associate { it.substringBefore('=').trim() to it.substringAfter('=').trim() }
                .filterKeys { System.getenv(it) == null },
        )
    }
}
