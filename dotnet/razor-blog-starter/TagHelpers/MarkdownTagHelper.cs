using Markdig;
using Markdig.Syntax;
using Markdig.Syntax.Inlines;
using Microsoft.AspNetCore.Razor.TagHelpers;

namespace RazorBlogStarter.TagHelpers;

/// <summary>
/// A markdown field, such as a post's body or an author's bio: <c>&lt;markdown text="@post.Body" /&gt;</c>.
/// HTML written into the text is shown as text, not run, and a link can only go to a web page
/// or an email address, so an entry cannot add scripts to the page.
/// </summary>
[HtmlTargetElement("markdown", TagStructure = TagStructure.WithoutEndTag)]
public sealed class MarkdownTagHelper : TagHelper
{
    private static readonly MarkdownPipeline Pipeline = new MarkdownPipelineBuilder().DisableHtml().Build();

    public string? Text { get; set; }

    public override void Process(TagHelperContext context, TagHelperOutput output)
    {
        if (string.IsNullOrEmpty(Text))
        {
            output.SuppressOutput();
            return;
        }

        var document = Markdown.Parse(Text, Pipeline);
        foreach (var link in document.Descendants<LinkInline>().Where(link => !IsSafe(link.Url)))
        {
            link.Url = "";
        }
        foreach (var link in document.Descendants<AutolinkInline>().Where(link => !IsSafe(link.Url)))
        {
            link.Url = "";
        }

        output.TagName = "div";
        output.TagMode = TagMode.StartTagAndEndTag;
        output.Attributes.SetAttribute("class", "prose");
        output.Content.SetHtmlContent(document.ToHtml(Pipeline));
    }

    /// <summary>A link to another page of the site, a web page, or an email address: never <c>javascript:</c>.</summary>
    private static bool IsSafe(string? url) =>
        Uri.TryCreate(url, UriKind.RelativeOrAbsolute, out var uri)
            && (!uri.IsAbsoluteUri || uri.Scheme is "http" or "https" or "mailto");
}
