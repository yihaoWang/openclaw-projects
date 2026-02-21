# Git-to-Viral 🚀

**Turn your GitHub repo into viral social media content automatically.**

## Usage
1. Clone this repo.
2. Run `npm install`.
3. Run `node index.js <repo-url>`.

## Example
```bash
node index.js https://github.com/facebook/react -o ./my-blog-post
```

## Features
- **Blog Generation**: Creates a Markdown blog post template.
- **Twitter Thread**: Writes a 5-tweet thread highlighting key tech.
- **LinkedIn Post**: Professional post for your network.

## Roadmap (Night Shift Iteration)
- [ ] Add real `git clone` support.
- [ ] Parse `package.json` for accurate stack detection.
- [ ] Add OpenAI/Gemini integration for deep code analysis.
