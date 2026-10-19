using RazorBlogStarter;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();
builder.Services.AddSingleton<Site>();

// The site's Coho client, for every page. What it reads, and with which credential, comes
// from configuration, not the code: with a preview token it reads dev or a branch, live;
// with a delivery key, released content. On your machine, they are user secrets.
builder.Services.AddCoho();

// In production, a page is rendered again with fresh content at most once a minute.
// In development every request renders, so it always shows the latest.
builder.Services.AddOutputCache(options => options.AddBasePolicy(policy => policy.Expire(TimeSpan.FromSeconds(60))));

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseOutputCache();
}

// An address with nothing at it shows the Not found page.
app.UseStatusCodePagesWithReExecute("/NotFound");

app.MapStaticAssets();
app.MapRazorPages().WithStaticAssets();

app.Run();
