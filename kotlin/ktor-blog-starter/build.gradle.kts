plugins {
    application
    kotlin("jvm") version "2.4.21"
    kotlin("plugin.serialization") version "2.4.21"
}

repositories()
{
    mavenCentral()
}

dependencies()
{
    implementation("io.ktor:ktor-server-netty:3.6.0")
    implementation("io.ktor:ktor-server-content-negotiation:3.6.0")
    implementation("io.ktor:ktor-serialization-kotlinx-json:3.6.0")
    implementation("io.ktor:ktor-server-status-pages:3.6.0")
    implementation("ch.qos.logback:logback-classic:1.6.5")
    // For markdown fields, such as a post's body: see Site.kt.
    implementation("org.commonmark:commonmark:0.30.1")
}

kotlin()
{
    jvmToolchain(21)
}

application()
{
    mainClass.set("com.example.blog.ApplicationKt")
}

// The Coho values, from .env, which git ignores. A variable already set, such as
// COHO_REF=feature/x ./gradlew run, wins over the same one in .env.
tasks.named<JavaExec>("run")
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
