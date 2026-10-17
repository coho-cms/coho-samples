/** The site's name, shown in the header and in every page's title. */
export const siteName = 'Field notes';

/** The locale the content is read in, for the page's language and its dates. */
export const locale = process.env.COHO_LOCALE || 'en-US';

/** A date and time such as `2026-10-01T09:00:00Z`, as a date such as `October 1, 2026`. */
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(locale, { dateStyle: 'long', timeZone: 'UTC' });
}
