function deleteItem(itemId){
    fetch("/delete-item", { // sends post request to delete-item endpoint
        method: "POST",
        body: JSON.stringify({itemId:itemId})
    }).then((_res) => {
        window.location.href = "/"   // reloads window (home)
    });
}

