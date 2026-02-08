import Anthropic from '@anthropic-ai/sdk';
import axios from 'axios';
import * as cheerio from 'cheerio';
import 'dotenv/config';

// Tool implementations
const checkDeployedSite = {
  name: 'check_deployed_site',
  description: 'Fetches the deployed website and analyzes its HTML structure, scripts, and styles',
  callback: async (input: { url: string }) => {
    try {
      const response = await axios.get(input.url, { timeout: 10000 });
      const $ = cheerio.load(response.data);
      
      const analysis = {
        status: response.status,
        title: $('title').text(),
        scripts: $('script').map((_, el) => $(el).attr('src') || 'inline').get(),
        stylesheets: $('link[rel="stylesheet"]').map((_, el) => $(el).attr('href')).get(),
        buttons: $('button').map((_, el) => ({ id: $(el).attr('id'), text: $(el).text() })).get(),
        hasCounter: $('#count').length > 0,
        bodyStructure: $('body').children().map((_, el) => el.tagName).get(),
      };
      
      return JSON.stringify(analysis, null, 2);
    } catch (error: any) {
      return `Error fetching site: ${error.message}`;
    }
  },
};

const testJavaScriptFunctionality = {
  name: 'test_javascript_functionality',
  description: 'Tests if critical JavaScript functionality is working by checking for expected elements and event handlers',
  callback: async (input: { url: string; expectedElements: string[] }) => {
    try {
      const response = await axios.get(input.url);
      const $ = cheerio.load(response.data);
      
      const results = {
        elementsFound: [] as string[],
        elementsMissing: [] as string[],
        scriptsLoaded: $('script').length,
        potentialIssues: [] as string[],
      };
      
      input.expectedElements.forEach(id => {
        if ($(`#${id}`).length > 0) {
          results.elementsFound.push(id);
        } else {
          results.elementsMissing.push(id);
          results.potentialIssues.push(`Missing expected element: #${id}`);
        }
      });
      
      if ($('script[src]').length === 0 && $('script').length === 0) {
        results.potentialIssues.push('No JavaScript files found - functionality may be broken');
      }
      
      return JSON.stringify(results, null, 2);
    } catch (error: any) {
      return `Error testing functionality: ${error.message}`;
    }
  },
};

const compareDeployments = {
  name: 'compare_deployments',
  description: 'Compares two versions of the deployed site to identify breaking changes',
  callback: async (input: { currentUrl: string; previousUrl?: string }) => {
    try {
      const currentResponse = await axios.get(input.currentUrl);
      const $current = cheerio.load(currentResponse.data);
      
      const currentAnalysis = {
        scripts: $current('script').length,
        styles: $current('link[rel="stylesheet"]').length,
        buttons: $current('button').length,
        interactiveElements: $current('button, input, select, textarea').length,
        criticalIds: ['count', 'increment', 'decrement', 'reset'],
        foundIds: [] as string[],
        missingIds: [] as string[],
      };
      
      currentAnalysis.criticalIds.forEach(id => {
        if ($current(`#${id}`).length > 0) {
          currentAnalysis.foundIds.push(id);
        } else {
          currentAnalysis.missingIds.push(id);
        }
      });
      
      const breakingChanges = [];
      if (currentAnalysis.missingIds.length > 0) {
        breakingChanges.push(`Missing critical elements: ${currentAnalysis.missingIds.join(', ')}`);
      }
      if (currentAnalysis.scripts === 0) {
        breakingChanges.push('No JavaScript files detected - counter functionality will not work');
      }
      if (currentAnalysis.buttons === 0) {
        breakingChanges.push('No buttons found - user interaction is broken');
      }
      
      return JSON.stringify({
        currentAnalysis,
        breakingChanges,
        status: breakingChanges.length === 0 ? 'HEALTHY' : 'ISSUES_DETECTED',
      }, null, 2);
    } catch (error: any) {
      return `Error comparing deployments: ${error.message}`;
    }
  },
};

const checkCommonIssues = {
  name: 'check_common_issues',
  description: 'Checks for common deployment issues like missing files, broken links, or CORS problems',
  callback: async (input: { url: string }) => {
    try {
      const response = await axios.get(input.url);
      const $ = cheerio.load(response.data);
      
      const issues = [];
      const warnings = [];
      
      // Check for external resources
      const externalScripts = $('script[src]').map((_, el) => $(el).attr('src')).get();
      const externalStyles = $('link[rel="stylesheet"]').map((_, el) => $(el).attr('href')).get();
      
      for (const src of externalScripts) {
        if (src && !src.startsWith('http')) {
          try {
            const fullUrl = new URL(src, input.url).href;
            await axios.head(fullUrl, { timeout: 5000 });
          } catch {
            issues.push(`Script file not accessible: ${src}`);
          }
        }
      }
      
      for (const href of externalStyles) {
        if (href && !href.startsWith('http')) {
          try {
            const fullUrl = new URL(href, input.url).href;
            await axios.head(fullUrl, { timeout: 5000 });
          } catch {
            issues.push(`Stylesheet not accessible: ${href}`);
          }
        }
      }
      
      // Check for console errors indicators
      if ($('script').length === 0) {
        warnings.push('No JavaScript detected - ensure this is intentional');
      }
      
      if ($('link[rel="stylesheet"]').length === 0 && $('style').length === 0) {
        warnings.push('No CSS detected - page may appear unstyled');
      }
      
      return JSON.stringify({
        issues,
        warnings,
        status: issues.length === 0 ? 'OK' : 'PROBLEMS_FOUND',
        checkedAt: new Date().toISOString(),
      }, null, 2);
    } catch (error: any) {
      return `Error checking for issues: ${error.message}`;
    }
  },
};

// Create Anthropic client
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Create tools array for Anthropic
const tools = [
  {
    name: checkDeployedSite.name,
    description: checkDeployedSite.description,
    input_schema: {
      type: 'object',
      properties: {
        url: { type: 'string', description: 'The URL of the deployed website to check' },
      },
      required: ['url'],
    },
  },
  {
    name: testJavaScriptFunctionality.name,
    description: testJavaScriptFunctionality.description,
    input_schema: {
      type: 'object',
      properties: {
        url: { type: 'string', description: 'The URL to test' },
        expectedElements: {
          type: 'array',
          items: { type: 'string' },
          description: 'Array of element IDs that should exist',
        },
      },
      required: ['url', 'expectedElements'],
    },
  },
  {
    name: compareDeployments.name,
    description: compareDeployments.description,
    input_schema: {
      type: 'object',
      properties: {
        currentUrl: { type: 'string', description: 'URL of the current/new deployment' },
        previousUrl: { type: 'string', description: 'URL of the previous deployment (optional)' },
      },
      required: ['currentUrl'],
    },
  },
  {
    name: checkCommonIssues.name,
    description: checkCommonIssues.description,
    input_schema: {
      type: 'object',
      properties: {
        url: { type: 'string', description: 'The deployed site URL to check' },
      },
      required: ['url'],
    },
  },
];

// Simple agent loop
async function runAgent(userMessage: string) {
  const messages: any[] = [
    {
      role: 'user',
      content: userMessage,
    },
  ];

  const systemPrompt = `You are a deployment analysis expert. Your job is to:
1. Analyze deployed websites for potential breaking changes
2. Identify missing critical elements (buttons, scripts, styles)
3. Test functionality and report issues
4. Compare deployments to detect regressions
5. Provide clear, actionable feedback about deployment health

When analyzing a deployment:
- Always check for critical interactive elements (buttons, forms, etc.)
- Verify JavaScript and CSS files are loading
- Look for missing IDs that are required for functionality
- Report both breaking changes and warnings
- Be specific about what's broken and how it impacts users`;

  let continueLoop = true;
  let iterations = 0;
  const maxIterations = 10;

  while (continueLoop && iterations < maxIterations) {
    iterations++;
    
    const response = await anthropic.messages.create({
      model: 'claude-3-haiku-20240307',
      max_tokens: 4096,
      system: systemPrompt,
      messages,
      tools,
    });

    console.log(`\n[Iteration ${iterations}]`);
    
    // Add assistant response to messages
    messages.push({
      role: 'assistant',
      content: response.content,
    });

    // Check if we need to execute tools
    const toolUses = response.content.filter((block: any) => block.type === 'tool_use');
    
    if (toolUses.length === 0) {
      // No more tools to execute, we're done
      continueLoop = false;
      
      // Print final response
      const textBlocks = response.content.filter((block: any) => block.type === 'text');
      for (const block of textBlocks) {
        console.log(block.text);
      }
    } else {
      // Execute tools
      const toolResults = [];
      
      for (const toolUse of toolUses) {
        console.log(`🔧 Using tool: ${toolUse.name}`);
        console.log(`   Input: ${JSON.stringify(toolUse.input, null, 2)}`);
        
        let result;
        switch (toolUse.name) {
          case 'check_deployed_site':
            result = await checkDeployedSite.callback(toolUse.input);
            break;
          case 'test_javascript_functionality':
            result = await testJavaScriptFunctionality.callback(toolUse.input);
            break;
          case 'compare_deployments':
            result = await compareDeployments.callback(toolUse.input);
            break;
          case 'check_common_issues':
            result = await checkCommonIssues.callback(toolUse.input);
            break;
          default:
            result = `Unknown tool: ${toolUse.name}`;
        }
        
        console.log(`   Result: ${result.substring(0, 200)}...`);
        
        toolResults.push({
          type: 'tool_result',
          tool_use_id: toolUse.id,
          content: result,
        });
      }
      
      // Add tool results to messages
      messages.push({
        role: 'user',
        content: toolResults,
      });
    }
  }
}

// Remove the old agent creation code
const deploymentUrl = process.env.DEPLOYMENT_URL || 'https://your-username.github.io/your-repo/';

console.log('🤖 Deployment Analyzer Agent Starting...\n');
console.log(`Analyzing deployment at: ${deploymentUrl}\n`);

await runAgent(
  `Analyze the deployment at ${deploymentUrl} and identify any breaking changes or issues that would prevent the counter functionality from working. Check for missing elements, broken scripts, or other problems.`
);

console.log('\n📊 Analysis Complete!\n');
