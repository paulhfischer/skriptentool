const dropdownHeaderElement = (filterDropdownItems: (filter: string) => void): HTMLDivElement => {
    const inputGroupText = document.createElement('div');
    inputGroupText.classList.add('input-group-text');
    inputGroupText.innerHTML = '<i class="fas fa-search"></i>';

    const inputGroupPrepend = document.createElement('div');
    inputGroupPrepend.classList.add('input-group-prepend');
    inputGroupPrepend.appendChild(inputGroupText);

    const input = document.createElement('input');
    input.classList.add('form-control', 'form-control-sm');
    input.type = 'text';
    input.placeholder = document.getElementById('select-script')!.dataset.search!;
    input.autofocus = true;
    input.addEventListener('keyup', () => filterDropdownItems(input.value));

    const inputGroup = document.createElement('div');
    inputGroup.classList.add('input-group');
    inputGroup.appendChild(inputGroupPrepend);
    inputGroup.appendChild(input);

    const dropdownHeader = document.createElement('div');
    dropdownHeader.classList.add('dropdown-header');
    dropdownHeader.appendChild(inputGroup);

    return dropdownHeader;
};

const dropdownItemElement = (value: string, text: string, active: boolean): HTMLDivElement => {
    const dropdownItem = document.createElement('div');
    dropdownItem.classList.add('dropdown-item');
    if (active) dropdownItem.classList.add('active');
    dropdownItem.dataset.value = value;
    dropdownItem.innerText = text;

    return dropdownItem;
};

const dropdownMenuElement = (
    dropdownID: string,
    dropdownHeader: HTMLDivElement,
    dropdownItems: Array<HTMLDivElement>,
    setValue: (value: string) => void,
): HTMLDivElement => {
    const dropdownOptions = document.createElement('div');
    dropdownOptions.classList.add('dropdown-options');
    dropdownItems.forEach((dropdownItem) => {
        dropdownOptions.appendChild(dropdownItem);
        dropdownItem.addEventListener('click', () => setValue(dropdownItem.dataset.value!));
    });

    const dropdownMenu = document.createElement('div');
    dropdownMenu.classList.add('dropdown-menu');
    dropdownMenu.setAttribute('aria-labelledby', dropdownID);
    if (dropdownItems.length > 5) dropdownMenu.appendChild(dropdownHeader);
    dropdownMenu.appendChild(dropdownOptions);

    return dropdownMenu;
};

const dropdownElement = (select: HTMLSelectElement): HTMLDivElement => {
    const id = `dropdown-${select.id}`;

    const customSelect = document.createElement('div');
    customSelect.classList.add('custom-select');
    customSelect.id = id;
    customSelect.dataset.toggle = 'dropdown';
    customSelect.dataset.flip = 'false';
    customSelect.ariaHasPopup = 'true';
    customSelect.ariaExpanded = 'false';
    customSelect.innerText = select.options[select.selectedIndex].text;

    const dropdownItems = Array.from(select.options).map((option) =>
        dropdownItemElement(option.value, option.text, option.value === select.value),
    );
    const filterDropdownItems = (filter: string) => {
        dropdownItems.forEach((dropdownItem) => {
            if (dropdownItem.innerText.toLowerCase().indexOf(filter.toLowerCase()) > -1) {
                /* eslint-disable-next-line no-param-reassign */
                dropdownItem.hidden = false;
            } else {
                /* eslint-disable-next-line no-param-reassign */
                dropdownItem.hidden = true;
            }
        });
    };
    const setValue = (value: string) => {
        dropdownItems.forEach((dropdownItem) => {
            if (dropdownItem.dataset.value === value) {
                dropdownItem.classList.add('active');
                customSelect.innerText = dropdownItem.innerText;
            } else {
                dropdownItem.classList.remove('active');
            }
        });
        /* eslint-disable-next-line no-param-reassign */
        select.value = value;
    };

    const dropdownHeader = dropdownHeaderElement(filterDropdownItems);

    const dropdownMenu = dropdownMenuElement(id, dropdownHeader, dropdownItems, setValue);

    const dropdown = document.createElement('div');
    dropdown.classList.add('dropdown', 'dropdown-select');
    dropdown.appendChild(customSelect);
    dropdown.appendChild(dropdownMenu);

    return dropdown;
};

const render = (): void => {
    const selects = Array.from(
        document.getElementsByClassName('custom-select') as HTMLCollectionOf<HTMLSelectElement>,
    );

    selects.forEach((select) => {
        /* eslint-disable-next-line no-param-reassign */
        select.hidden = true;
        select.insertAdjacentElement('afterend', dropdownElement(select));
    });
};

render();

export {};
