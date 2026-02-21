#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { program } = require('commander');
const { analyzeRepo } = require('./lib/analyzer');
const { generateContent } = require('./lib/generator');

program
  .name('git-to-viral')
  .description('Transform a GitHub repo into a high-converting technical blog post & Twitter thread')
  .version('1.0.0');

program
  .argument('<repo-url>', 'GitHub repository URL (e.g., https://github.com/facebook/react)')
  .option('-o, --output <dir>', 'Output directory', './output')
  .action(async (repoUrl, options) => {
    console.log(`🚀 Night Shift Agent: Analyzing ${repoUrl}...`);
    
    // 1. Analyze the repo (simulated LLM or heuristic based)
    const analysis = await analyzeRepo(repoUrl);
    console.log(`✅ Analysis complete: Found ${analysis.filesCount} files, identified stack: ${analysis.stack.join(', ')}`);

    // 2. Generate content
    console.log('📝 Drafting blog post and social media content...');
    const content = await generateContent(analysis);

    // 3. Save to files
    if (!fs.existsSync(options.output)) {
      fs.mkdirSync(options.output, { recursive: true });
    }
    
    fs.writeFileSync(path.join(options.output, 'blog-post.md'), content.blog);
    fs.writeFileSync(path.join(options.output, 'twitter-thread.md'), content.twitter);
    fs.writeFileSync(path.join(options.output, 'linkedin-post.md'), content.linkedin);

    console.log(`✨ Success! Content saved to ${options.output}`);
    console.log('   - blog-post.md');
    console.log('   - twitter-thread.md');
    console.log('   - linkedin-post.md');
  });

program.parse();
