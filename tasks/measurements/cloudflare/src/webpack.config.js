module.exports = {
  entry: './index.js',
  output: {
    filename: 'bundle.js',
    path: "/tmp/cloudflare/speedtest/",
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
        },
      },
    ],
  },
};
