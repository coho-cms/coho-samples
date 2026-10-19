using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace RazorBlogStarter.Pages.Posts;

/// <summary>A post, with its author and tags.</summary>
public sealed class PostModel(Coho coho) : PageModel
{
    /// <summary>The post. Set by <see cref="OnGetAsync"/> before the page renders.</summary>
    public BlogPost Post { get; private set; } = null!;

    public async Task<IActionResult> OnGetAsync(string slug, CancellationToken cancellationToken)
    {
        // Depth 1 brings the post's author, tags and related posts in the same request.
        var post = await coho.BlogPost.BySlugAsync(slug, new ReadOptions { Depth = 1 }, cancellationToken);
        if (post is null)
        {
            return NotFound();
        }
        Post = post;
        return Page();
    }
}
