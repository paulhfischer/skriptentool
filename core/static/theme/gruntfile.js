module.exports = function (grunt) {
    grunt.initConfig({
        sass: {
            dist: {
                options: {
                    style: 'compressed',
                    'no-source-map': true
                },
                files: {
                    '../style.css': 'scss/style.scss'
                }
            }
        },
        autoprefixer: {
            dist: {
                files: {
                    '../style.css': '../style.css'
                }
            }
        },
        watch: {
            css: {
                files: 'scss/*.scss',
                tasks: ['sass', 'autoprefixer']
            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-autoprefixer');
    grunt.registerTask('default', ['watch']);
};