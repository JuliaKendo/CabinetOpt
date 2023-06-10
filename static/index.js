const loadJson = function(selector) {
    return JSON.parse(document.querySelector(selector).getAttribute('data-json'));
}

const removeErrors = function() {
    Array.from(
        document.getElementsByClassName('errors')
    ).forEach((item) => {
        while (item.firstChild) {
            item.removeChild(item.firstChild);
        }
    });
}


const showErrors = function(errors) {
    removeErrors();
    $.each(JSON.parse(errors), (name, error) => {
        error.forEach((item) => {
            const newError = document.createElement('p');
            newError.textContent = item['message'];
            Array.from(
                document.getElementsByClassName(`${name}-error`)
            ).forEach((element) => {
                element.appendChild(newError);
            });
        });
    });
}


const showModalForm = function(formId) {
    $(`#${formId}`).on('shown.bs.modal', (event) => {
        $.ajax({
            url: event.relatedTarget.getAttribute('data-url'),
            success: (data) => {
                $(`#${formId}`).html(data);
            },
            error: (xhr, status, error) => {
                alert('Ошибка: ' + error);
            }
        });
    });
    updateModalForm(formId);   
}


const updateModalForm = function(formId) {
    $(`#${formId}`).on('submit', (event) => {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: event.target.action,
            data: $(`.${formId}`).serialize(),
            success: (data) => {
                if(data['errors']) {
                    showErrors(data['errors']);
                    data['errors'] = {}
                } else {
                    $('.modal').modal('hide');
                    location.reload();
                }
            },
            error: (response) => {
                const errors = JSON.parse(response.responseText).errors;
                showErrors(errors);
            }
        });
    });
}


const updateForm = function(formId) {
    $.ajax({
        url: $(`#${formId}`).attr('action'),
        success: (data) => {
            $(`#${formId}`).html(data);
        },
        error: (xhr, status, error) => {
            alert('Ошибка: ' + error);
        }
    });
}


const extractContent = function(html, elementId){
    const DOMModel = new DOMParser()
        .parseFromString(html, 'text/html');
    return DOMModel.getElementById(elementId).innerHTML;
}


const updateElement = function(elementId, data) {
    $.ajax({
        type: 'POST',
        data: data,
        cache: false,
        success: (data) => {
            $(`#${elementId}`).html(
                extractContent(data, elementId)
        )},
        error: (xhr, status, error) => {
            alert('Ошибка: ' + error);
        }
    });
}


const toggleClassButton = function(target, fromClass, toClass) {
    const classes = target.classList;
    if ( classes.contains(fromClass) ) {
        classes.add(toClass);
        classes.remove(fromClass);
    } else if ( classes.contains(toClass) ) {
        classes.add(fromClass);
        classes.remove(toClass);
    }
}

const showElement = function(elementId, show) {
    document.getElementById(elementId).style.display = show ? 'block' : 'none';
}

const switchCartView = function(checked) {
    if (checked) {
        document.getElementById('products').style.display = 'none';
        document.getElementById('cart-table').style.display = 'block';
    } else {
        document.getElementById('products').style.display = 'block';
        document.getElementById('cart-table').style.display = 'none';
    }
    localStorage.setItem('cartView', checked);
}


const createCartViewInput = function() {
    const checkboxElement = document.createElement('input');
    checkboxElement.id = 'cartView';
    checkboxElement.type = 'checkbox';
    checkboxElement.classList.add('custom-control-input');
    if (localStorage.getItem('cartView') === 'true') {
        checkboxElement.checked = true;
    }
    const labelElement = document.createElement('label');
    labelElement.classList.add('custom-control-label');
    labelElement.textContent = 'компактный вид';
    labelElement.setAttribute('for', checkboxElement.id);

    const cartViewArea = document.getElementById('cartViewArea');
    if (cartViewArea) {
        cartViewArea.appendChild(checkboxElement);
        cartViewArea.appendChild(labelElement);
    }
    switchCartView(checkboxElement.checked);
}

const fillCollectionTree = (jsonCollection, collectionList, excludedCollection) => {

    Object.keys(jsonCollection).forEach((key) => {
        const node = jsonCollection[key];
        for (const nodeName in node) {
            if (node.hasOwnProperty(nodeName)) {
                innerHTML = 
                    `<li class="list-group-item"><span class="collection-box">${nodeName}</span>
                        <ul class="collection-nested list-group list-group-flush">`;

                node[nodeName].forEach((item) => {
                    const checked = (excludedCollection.includes(`collection-${item['id']}`)) ? "" : "checked"
                    innerHTML += 
                        `<li class="list-group-item" style="padding-top: 5px; padding-bottom: 5px;">
                            <input class="form-check-input me-1 switch-change" type="checkbox" value="collection" id="collection-${item['id']}" ${checked}>
                            <label class="form-check-label" for="collection-${item['id']}" style="font-size: smaller;">${item['name']}</label></li>`;

                });
                innerHTML += `</ul></li>`;
                collectionList.innerHTML += innerHTML;
            }
          }
    });

}

const createBrandAndCollectionLists = function() {
    const excludedВrands = localStorage.getItem('excludedВrands');
    const excludedCollection = localStorage.getItem('excludedCollection');
    const jsonBrands = loadJson('#jsonBrands');
    const jsonCollections = loadJson('#jsonCollections');

    const brandList = document.querySelector('.brend-group'); 
    jsonBrands.forEach((brand) => {
        const checked = (excludedВrands.includes(`brand-${brand.id}`)) ? "" : "checked"
        brandList.innerHTML += 
        `<li class="list-group-item">
            <input class="form-check-input me-1 switch-change" type="checkbox" value="brand" id="brand-${brand.id}" ${checked}>
            <label class="form-check-label" for="brand-${brand.id}">${brand.name}</label>
        </li>`
    });

    const collectionList = document.querySelector('.collection-group'); 
    fillCollectionTree(jsonCollections, collectionList, excludedCollection);

    updateElement('products', {
        'csrfmiddlewaretoken' : document.querySelector('input[name="csrfmiddlewaretoken"]').value,
        'data': JSON.stringify({
            'brand': excludedВrands.split(','),
            'collection': excludedCollection.split(',')
        })
    });
    
}


const updateItem = function(element) {
    const partsOfId = element.id.split('-');
    const quantityId = `${partsOfId.slice(0, partsOfId.length-1).join('-')}-quantity`;
    const priceId    = `${partsOfId.slice(0, partsOfId.length-1).join('-')}-price`;
    const sumId      = `${partsOfId.slice(0, partsOfId.length-1).join('-')}-sum`;    
    if (partsOfId[partsOfId.length-1] === 'quantity') {
        const price = document.getElementById(priceId);
        const sum = document.getElementById(sumId);
        sum.value = price.value * element.value;
    }
    else if (partsOfId[partsOfId.length-1] === 'price') {
        const quantity = document.getElementById(quantityId);
        const sum = document.getElementById(sumId);
        sum.value = quantity.value * element.value;
    }
    else if (partsOfId[partsOfId.length-1] === 'sum') {
        const quantity = document.getElementById(quantityId);
        const price = document.getElementById(priceId);
        price.value = element.value / (quantity.value != 0 ? quantity.value : 1);
    }
    else if (partsOfId[partsOfId.length-1] === 'price_type') {
    }
}


const addEvents = function() {

    $('.order-row').click((event) => {
        window.document.location = event.currentTarget.dataset.href
    });

    $('#cartView').click((event) => {
        switchCartView(event.currentTarget.checked);
    });

    $('#Brend').on('click', (event) => {
        toggleClassButton(event.currentTarget, 'btn-success', 'btn-outline-success');
        toggleClassButton(
            document.getElementById('Assortment'), 'btn-outline-warning', 'btn-warning'
        );
        if ( event.currentTarget.classList.contains('btn-success') ) {
            showElement('brend-group', true);
            showElement('collection-group', false);
        } else {
            showElement('brend-group', false);
            showElement('collection-group', true);
        }
    })
    
    $('#Assortment').on('click', (event) => {
        toggleClassButton(event.currentTarget, 'btn-warning', 'btn-outline-warning');
        toggleClassButton(
            document.getElementById('Brend'), 'btn-outline-success', 'btn-success'
        );
        if ( event.currentTarget.classList.contains('btn-warning') ) {
            showElement('collection-group', true);
            showElement('brend-group', false);
        } else {
            showElement('collection-group', false);
            showElement('brend-group', true);
        }
    })
    
    $('.switch-change').on('change', (event) => {
        data = {'brand': [], 'collection': []};
        Array.from(
            document.getElementsByClassName('switch-change')
        ).forEach((item) => {
            if ( item.checked ) {
                return;
            }
            data[item.value].push(item.id);
        });
        localStorage.setItem('excludedВrands', data.brand);
        localStorage.setItem('excludedCollection', data.collection);
        
        updateElement('products', {
            'csrfmiddlewaretoken' : document.querySelector('input[name="csrfmiddlewaretoken"]').value,
            'data': JSON.stringify(data)
        });
    })

    const toggler = document.getElementsByClassName("collection-box"); let i;
    for (i = 0; i < toggler.length; i++) {
      toggler[i].addEventListener('click', (event) => {
        if (event.target.parentElement) {
            event.target.parentElement.querySelector('.collection-nested')?.classList.toggle('collection-active');
            event.target.classList.toggle('collection-open-box');
        }
      });
    }

}


$(window).on("load", function() {
    if (localStorage.getItem('cartView') === null) {
        localStorage.setItem('cartView', false);
    }
    if (localStorage.getItem('excludedВrands') === null) {
        localStorage.setItem('excludedВrands', new Array());
    }
    if (localStorage.getItem('excludedCollection') === null) {
        localStorage.setItem('excludedCollection', new Array());
    }
});


$(document).ready(() => {
    showModalForm('loginForm'); 
    showModalForm('regRequestForm');
    updateForm('contactForm');

    if (document.location.pathname === "/cart/") {
        createCartViewInput();
    } else if (document.location.pathname === "/catalog/products/") {
        createBrandAndCollectionLists();
    }
    addEvents();
})

