function deleteItem(itemId){
    fetch("/delete-item", { // sends post request to delete-item endpoint
        method: "POST",
        body: JSON.stringify({itemId:itemId})
    }).then((_res) => {
        window.location.href = "/"   // reloads window (home)
    });
}


// make request to backend to update user items in db
// called from frontend (home page) and is on page load
// need a function on the backend that this JS function can access - backend will handle DB interaction
function updateItems(date){
    fetch("/update-items", {
        method: "POST",
        body: JSON.stringify({date:date})
    }).then((_res) => {
        //window.location.href = "/" 
        // after response, reloads home page, but home page on load calls this function -> infinite loop
    });
}
