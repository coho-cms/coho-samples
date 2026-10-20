package com.example.blog;

import com.cohocms.delivery.CohoDeliveryException;
import com.cohocms.delivery.CohoEnvironment;
import com.yourorg.blogcontent.coho.Coho;
import java.util.Map;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** The service's Coho client, for every controller, and what a refusal from Coho answers. */
@Configuration
public class CohoConfiguration
{
    /**
     * What it reads, and with which credential, comes from the configuration, not the code: with
     * a preview token it reads dev or a branch, live; with a delivery key, released content. On
     * your machine, they are in .env, which ./gradlew bootRun reads.
     */
    @Bean
    public Coho coho(Environment environment)
    {
        return new Coho(CohoEnvironment.from(environment::getProperty));
    }

    /**
     * Coho refused a read, or could not be reached properly. It is this service's problem, not the
     * caller's, so it is a 502, with Coho's code for whoever reads the logs.
     */
    @RestControllerAdvice
    public static class Refusals
    {
        @ExceptionHandler(CohoDeliveryException.class)
        public ResponseEntity<Map<String, String>> refused(CohoDeliveryException error)
        {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY).body(Map.of("code", error.getCode(), "detail", String.valueOf(error.getMessage())));
        }
    }
}
