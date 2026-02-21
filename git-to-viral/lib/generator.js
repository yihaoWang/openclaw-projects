const { analyzeRepo } = require('./analyzer');

async function generateContent(analysis) {
  const { name, summary, stack, complexity } = analysis;

  const blogPost = `# 🚀 How We Built ${name}: A Deep Dive into ${stack[0]}\n\n## Introduction\nWelcome to a detailed technical breakdown of ${name}. This project is built using **${stack.join(', ')}** and focuses on...\n\n## Architecture\n- **Complexity**: ${complexity}\n- **Core Components**: ...\n\n## Key Learnings\n1. Use Docker for...\n2. Optimize React components by...\n\n## Conclusion\nCheck out the repo at github.com/${name}. Happy coding!\n`;

  const twitterThread = `🧵 1/5: Just explored ${name}! A fascinating ${stack[0]} project that solves...\n\n2/5: 🏗️ Tech Stack:\n- ${stack.join('\n- ')}\n\n3/5: 💡 Key Takeaway: Using Docker simplifies deployment by 10x.\n\n4/5: 🛠️ Complexity: ${complexity}. Perfect for mid-level devs.\n\n5/5: Check it out here: github.com/${name} #webdev #opensource #${stack[0].toLowerCase()}`;

  const linkedinPost = `🔥 New Project Discovery: ${name}\n\nI recently dove into the source code of ${name}, an impressive ${stack[0]} application.\n\nKey Highlights:\n- Modern stack: ${stack.join(', ')}\n- Clean architecture with ${complexity} complexity.\n\nIf you're a developer looking to learn ${stack[0]}, this repo is a goldmine.\n\n🔗 Link in comments! 👇\n#softwareengineering #${stack[0].toLowerCase()} #opensource`;

  return {
    blog: blogPost,
    twitter: twitterThread,
    linkedin: linkedinPost
  };
}

module.exports = { generateContent };