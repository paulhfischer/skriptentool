/* eslint "import/no-extraneous-dependencies": off */
/* eslint "import/no-unresolved": off */
/* eslint "global-require": off */
module.exports = {
    plugins: [
        require('autoprefixer'),
        require('cssnano'),
        require('postcss-discard-comments')({ removeAll: true }),
    ],
};
