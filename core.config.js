/* eslint "import/no-extraneous-dependencies": off */
/* eslint "import/no-unresolved": off */
const path = require('path');
const RemoveEmptyScriptsPlugin = require('webpack-remove-empty-scripts');
const TerserPlugin = require('terser-webpack-plugin');
const webpack = require('webpack');

const config = {
    entry: {
        style: './core/build/scss/style.scss',
    },

    output: {
        path: path.resolve(__dirname, 'core/static/'),
        filename: './js/[name].min.js',
    },

    module: {
        rules: [
            {
                test: /\.scss/,
                include: path.resolve(__dirname, 'core/build/scss/'),
                exclude: [],
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name: './css/[name].min.css',
                        },
                    },
                    'extract-loader',
                    'css-loader',
                    'postcss-loader',
                    'sass-loader',
                ],
            },
        ],
    },

    resolve: {
        modules: ['node_modules'],
        extensions: ['.js', '.css', '.scss'],
    },

    performance: {
        maxEntrypointSize: 1024000,
        maxAssetSize: 1024000,
    },

    stats: {
        colors: true,
        hash: false,
        version: false,
        timings: false,
        assets: true,
        modules: false,
        entrypoints: false,
        builtAt: false,
    },

    plugins: [
        new RemoveEmptyScriptsPlugin({
            silent: true,
        }),
    ],
};

module.exports = (env, argv) => {
    if (argv.mode === 'development') {
        config.devtool = 'inline-source-map';
    }

    if (argv.mode === 'production') {
        config.optimization = {
            minimize: true,
            minimizer: [
                new TerserPlugin({
                    terserOptions: {
                        output: {
                            comments: false,
                        },
                    },
                    extractComments: false,
                }),
            ],
        };

        config.plugins = [
            ...config.plugins,
            new webpack.ProgressPlugin({
                percentBy: 'entries',
            }),
        ];
    }

    return config;
};
