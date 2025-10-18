export default function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="container flex flex-col items-center justify-between gap-4 py-6 md:h-24 md:flex-row md:py-0">
        <div className="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            Built with Next.js 15, TypeScript, and shadcn/ui.
            <br className="hidden sm:inline" />
            Systech AI Assistant Dashboard v0.1.0
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <a
            href="/doc/api-specification"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            API Docs
          </a>
          <a
            href="https://github.com"
            className="text-sm text-muted-foreground hover:text-foreground"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}
