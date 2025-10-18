# Public Directory

This directory contains static assets for the Next.js application.

## Files

- `favicon.ico` - Website favicon (placeholder)
- `next.svg` - Next.js logo
- `vercel.svg` - Vercel logo

## Usage

Files in this directory are served statically from the root path `/` in your Next.js application.

For example:

- `public/favicon.ico` → accessible at `/favicon.ico`
- `public/images/logo.png` → accessible at `/images/logo.png`

## Adding Assets

To add new static assets:

1. Place files directly in this directory or create subdirectories
2. Reference them in your components using absolute paths starting with `/`

Example:

```tsx
<img src="/images/logo.png" alt="Logo" />
```

## Best Practices

- Use descriptive filenames
- Optimize images for web (compress, use appropriate formats)
- Consider using Next.js Image component for images
- Keep file sizes reasonable for fast loading
