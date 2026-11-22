const { copyFile, mkdir, readFile } = require('node:fs/promises');
const { join } = require('node:path');

const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const source = join(botDir, 'VIDEO.json');
const destination = join(outputDir, 'VIDEO.json');

async function main() {
  try {
    await mkdir(outputDir, { recursive: true });
    await copyFile(source, destination);
  } catch (error) {
    const problem = error instanceof Error ? error.message : String(error);
    console.error(`Failed to copy VIDEO.json from "${source}" to "${destination}": ${problem}`);
    process.exitCode = 1;
    return;
  }

  try {
    const video = JSON.parse(await readFile(destination, 'utf8'));
    if (!video || typeof video.url !== 'string' || video.url.trim() === '') {
      throw new Error('expected a non-empty string in the "url" field');
    }
    console.log(video.url);
  } catch (error) {
    const problem = error instanceof Error ? error.message : String(error);
    console.error(`Failed to read or validate copied VIDEO.json at "${destination}": ${problem}`);
    process.exitCode = 1;
  }
}

main();
