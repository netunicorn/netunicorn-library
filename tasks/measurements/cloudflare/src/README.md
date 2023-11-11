# Cloudflare speedtest netunicorn task sources

This folder contains source code for Cloudflare speedtest adapted as netunicorn task.

In particular, to run the speedtest, you need to bundle the cloudflare speedtest npm module with the index.js file that uses these code. When the HTML page inporting this bundle would be opened, the speedtest would be run and results would be assigned to the window variable testResults, and window.testFinished would be set to true.

Currently, the task refers to the bundled version of the speedtest module, which is located in the `dist` folder. To rebuild the bundle, run `npm run build` in the `tasks/measurements/cloudflare` folder.

The bundled version is published as "cloudflare-speedtest-bundle:0.1" release in the netunicorn-repo.

## How to bundle the speedtest module

If you want to change index.js, you'll need to create the new bundle. For this:
1. Install npm
2. Create a new npm project in the `tasks/measurements/cloudflare/src` folder: `npm init`
3. Install the required modules: `npm install @cloudflare/speedtest babel-loader webpack webpack-cli`
4. Modify `index.js` as needed.
5. Run `npx webpack` to create the bundle in the folder specified in the `webpack.config.js` file.
6. Publish your bundle somewhere and change the requirements of the corresponding netunicorn task to point to your new bundle.

