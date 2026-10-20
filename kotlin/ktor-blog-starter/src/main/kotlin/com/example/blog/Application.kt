package com.example.blog

import com.cohocms.delivery.CohoDeliveryException
import com.cohocms.delivery.CohoEnvironment
import com.yourorg.blogcontent.coho.Coho
import io.ktor.http.HttpStatusCode
import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.plugins.statuspages.StatusPages
import io.ktor.server.response.respond
import io.ktor.server.routing.get
import io.ktor.server.routing.routing
import kotlinx.serialization.json.Json

fun main()
{
    embeddedServer(Netty, port = System.getenv("PORT")?.toInt() ?: 8080, module = Application::module).start(wait = true)
}

/** The service: its routes, and the Coho client they read through. */
fun Application.module()
{
    // The service's Coho client, for every route. What it reads, and with which credential, comes
    // from the environment, not the code: with a preview token it reads dev or a branch, live;
    // with a delivery key, released content. On your machine, they are in .env, which
    // ./gradlew run reads.
    val coho = Coho(CohoEnvironment.fromEnvironment())

    install(ContentNegotiation)
    {
        json(Json { prettyPrint = true; explicitNulls = true })
    }
    install(StatusPages)
    {
        // Coho refused a read, or could not be reached properly. It is this service's problem, not
        // the caller's, so it is a 502, with Coho's code for whoever reads the logs.
        exception<CohoDeliveryException>()
        { call, error ->
            call.respond(HttpStatusCode.BadGateway, mapOf("code" to error.code, "detail" to error.message.orEmpty()))
        }
    }

    routing()
    {
        get("/")
        {
            call.respond(SiteInfo(name = Site.NAME, posts = "/posts"))
        }
        posts(coho)
    }
}
