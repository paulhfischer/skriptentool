const path = require('path');
const webpack = require('webpack');

const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const RemoveEmptyScriptsPlugin = require('webpack-remove-empty-scripts');

const config = {
    entry: {
        style: './core/build/scss/style.scss',
        select: './core/build/ts/select.ts',
    },

    output: {
        path: path.resolve(__dirname, 'core/static/'),
        filename: 'js/[name].min.js',
    },

    module: {
        rules: [
            {
                test: /\.ts$/,
                include: path.resolve(__dirname, 'core/build/ts/'),
                exclude: [],
                use: [
                    {
                        loader: 'babel-loader',
                        options: {
                            presets: ['@babel/preset-env', '@babel/preset-typescript'],
                            plugins: ['@babel/plugin-transform-runtime'],
                        },
                    },
                    'ts-loader',
                ],
            },
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
                new TerserPlugin({
                    terserOptions: {
                        output: {
                            comments: false,
                        },
                    },
                    extractComments: false,
                }),
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
