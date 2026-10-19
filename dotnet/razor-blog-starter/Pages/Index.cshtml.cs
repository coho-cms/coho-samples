using Microsoft.AspNetCore.Mvc.RazorPages;

namespace RazorBlogStarter.Pages;

/// <summary>The home page: the latest posts.</summary>
public sealed class IndexModel(Coho coho) : PageModel
{
    public IReadOnlyList<BlogPost> Posts { get; private set; } = [];

    public async Task OnGetAsync(CancellationToken cancellationToken)
    {
        // Newest first. Depth 1 brings each post's author and tags in the same request.
        var posts = await coho.BlogPost.ListAsync(new() { Order = BlogPost.SortBy.PublishedAt.Descending, Depth = 1 }, cancellationToken);
        Posts = posts.Items;
    }
}
