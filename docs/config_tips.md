# Sounder Configuration Tips

## About Presences

**Sounder** presences allow you to share through platforms such as Discord or expose an API what you are listening to at that moment.

## About CDNs

### What is a CDN?

A CDN, or Content Delivery Network, is a distributed network of servers that caches content closer to users, reducing latency and improving website performance. It essentially acts as a proxy, delivering web content like images, videos, and HTML files from servers located near the user's location, rather than from the website's origin server.

### What are CDNs used for in Sounder?

If you want to use presences like Discord to show what you are listening to in your profile, you will have to use a CDN if you want to show the cover image or miniature of the sound/song that is playing at that moment.

### How do I use CDNs?

Due to presences like Discord, it is necessary that the images are provided from an external URL, so it is mandatory to use a CDN. For this, you can use any of those supported by Sounder.

### Should I use API Keys to use a CDN?

Most of the CDNs that Sounder supports require some form of authentication, with the links available in the `.env` and `.env.example` files.

### About API Keys for CDNs

Some environment variables for API Keys like IMGUR's CND, you can define several Client IDs so that if you exceed the limit of requests in one account, you can have another one available.

You can add as many as you want. You can do this in the environment variables named in plural.