const path = require('path');
const webpack = require('webpack');

const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const RemoveEmptyScriptsPlugin = require('webpack-remove-empty-scripts');

const config = {
    entry: {
        style: './core/build/scss/style.scss',
    },

    output: {
        path: path.resolve(__dirname, 'core/static/'),
    },

    module: {
        rules: [
            {
                test: /\.scss/,
                include: path.resolve(__dirname, 'core/build/scss/'),
                exclude: [],
                use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader', 'sass-loader'],
            },
        ],
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
        new MiniCssExtractPlugin({
            filename: './css/[name].min.css',
        }),
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
                new CssMinimizerPlugin({
                    minimizerOptions: {
                        preset: [
                            'default',
                            {
                                discardComments: { removeAll: true },
                            },
                        ],
                    },
                }),
            ],
        };

        if (!process.env.CI) {
            config.plugins = [
                ...config.plugins,
                new webpack.ProgressPlugin({
                    percentBy: 'entries',
                }),
            ];
        }
    }

    return config;
};
