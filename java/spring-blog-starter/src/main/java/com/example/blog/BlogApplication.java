package com.example.blog;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** The service: its routes are in the controllers beside it, and its Coho client in CohoConfiguration. */
@SpringBootApplication
public class BlogApplication
{
    public static void main(String[] args)
    {
        SpringApplication.run(BlogApplication.class, args);
    }
}
