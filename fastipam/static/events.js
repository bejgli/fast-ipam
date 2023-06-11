document.body.addEventListener('htmx:beforeSwap', function(evt) {
    if(evt.detail.xhr.status === 422){
        evt.detail.isError = false;
        evt.detail.shouldSwap = true;
        evt.detail.target = htmx.find("#errors");
    } else if(evt.detail.xhr.status === 400){
        evt.detail.isError = false;
        evt.detail.shouldSwap = true;        
        evt.detail.target = htmx.find("#errors");
    } else if(evt.detail.xhr.status === 401){
        evt.detail.isError = false;
        evt.detail.shouldSwap = false;        
    } else if(evt.detail.xhr.status === 403){
        evt.detail.isError = false;
        evt.detail.shouldSwap = true;        
        evt.detail.target = htmx.find("#errors");
    }
});