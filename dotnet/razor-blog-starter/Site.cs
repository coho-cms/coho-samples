using System.Globalization;
using System.Text.RegularExpressions;

namespace RazorBlogStarter;

/// <summary>The site's name, its locale, and how dates look. Every view has it, as <c>Site</c>.</summary>
public sealed partial class Site(IConfiguration configuration)
{
    /// <summary>The site's name, shown in the header and in every page's title.</summary>
    public string Name => "Field notes";

    /// <summary>The locale the content is read in, for the page's language and its dates.</summary>
    public string Locale { get; } = configuration["COHO_LOCALE"] is { Length: > 0 } locale ? locale : "en-US";

    /// <summary>A date such as <c>October 1, 2026</c>, as the locale writes it, without the day of the week.</summary>
    public string FormatDate(DateTimeOffset date)
    {
        var culture = CultureInfo.GetCultureInfo(Locale);
        var pattern = DayOfWeek().Replace(culture.DateTimeFormat.LongDatePattern, "");
        return date.UtcDateTime.ToString(pattern, culture);
    }

    [GeneratedRegex(@"dddd,?\s*")]
    private static partial Regex DayOfWeek();
}
