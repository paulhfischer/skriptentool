function getDropdown(select) {
    // dropdown-items from options
    const options = [];
    $(select)
        .find('option')
        .each(() => {
            if ($(this).is(':selected')) {
                options.push(
                    `<div class="dropdown-item active" data-value="${$(this).val()}">${$(
                        this,
                    ).text()}</div>`,
                );
            } else {
                options.push(
                    `<div class="dropdown-item" data-value="${$(this).val()}">${$(
                        this,
                    ).text()}</div>`,
                );
            }
        });

    // search-field if more than 5 options
    let search = [];
    if ($(select).find('option').length > 5) {
        search = [
            '<div class="dropdown-header">',
            '<div class="input-group">',
            '<div class="input-group-prepend">',
            '<div class="input-group-text"><i class="fas fa-search"></i></div>',
            '</div>',
            `<input class="form-control form-control-sm" id="search-${
                select.id
            }" type="text" placeholder="${$('#select-script').data('search')}">`,
            '</div>',
            '</div>',
            '<div class="dropdown-divider"></div>',
        ];
    }

    // dropdown-menu with options and search-field
    const dropdown = [
        '<div class="dropdown dropdown-select">',
        `<div class="custom-select" id="dropdown-${select.id}" data-toggle="dropdown" data-flip="false" aria-haspopup="true" aria-expanded="false">`,
        $(select).find('option:selected').text(),
        '</div>',
        `<div class="dropdown-menu" aria-labelledby="dropdown-${select.id}">`,
        search.join('\n'),
        '<div class="dropdown-options">',
        options.join('\n'),
        '</div>',
        '</div>',
        '</div>',
    ].join('\n');

    return dropdown;
}

// custom select-fields with search option
$(window).on('load', () => {
    const originalSelects = $('.custom-select');

    // hide default select-fields
    originalSelects.hide();

    // add custom select-field
    originalSelects.after(() => {
        return getDropdown(this);
    });

    const customSelects = $('.dropdown-select');
    const customOptions = $('.dropdown-options > .dropdown-item');

    // focus input on dropdown
    customSelects.on('shown.bs.dropdown', (event) => {
        $(event.target).parent().find('.dropdown-menu input').focus();
    });

    // toggle items on search
    $('[id^="search-"]').on('keyup', () => {
        const value = $(this).val().toLowerCase();
        const inputID = $(this).attr('id').replace('search-', '');
        const options = customSelects.find(
            `[aria-labelledby="dropdown-${inputID}"] > .dropdown-options > .dropdown-item`,
        );

        options.filter(() => {
            return $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });

    // update on select
    customOptions.on('click', () => {
        const selectedOption = $(this);
        const value = selectedOption.data('value');
        const displayValue = selectedOption.text();
        const inputID = selectedOption
            .parent()
            .parent()
            .attr('aria-labelledby')
            .replace('dropdown-', '');

        selectedOption.parent().find('.dropdown-item').removeClass('active');
        selectedOption.addClass('active');

        originalSelects.filter(`#${inputID}`).val(value);
        customSelects.find(`#dropdown-${inputID}`).text(displayValue);
    });
});
