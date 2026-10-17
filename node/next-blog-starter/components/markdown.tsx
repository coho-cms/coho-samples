import ReactMarkdown from 'react-markdown';

/**
 * A markdown field, such as a post's body or an author's bio. HTML written into the
 * text is shown as text, not run, so an entry cannot add scripts to the page.
 */
export function Markdown({ children }: { children?: string }) {
  if (!children) return null;
  return (
    <div className="prose">
      <ReactMarkdown>{children}</ReactMarkdown>
    </div>
  );
}
