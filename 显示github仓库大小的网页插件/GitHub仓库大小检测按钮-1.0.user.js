// ==UserScript==
// @name         GitHub仓库大小检测按钮
// @namespace    zuxtuo-namespace
// @version      1.1
// @description  Adds a red button in the top right corner of GitHub repository pages to display the repository size information in MB.
// @author       ZUXTUO
// @match        https://github.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_addStyle
// ==/UserScript==

(function() {
    'use strict';

    // Check if the current page is a GitHub repository page
    if (isRepositoryPage()) {
        // Get the repository owner and name from the URL
        const repositoryInfo = getRepositoryInfo();
        const owner = repositoryInfo[0];
        const name = repositoryInfo[1];

        // Make a request to the GitHub API to fetch repository information
        GM_xmlhttpRequest({
            method: 'GET',
            url: `https://api.github.com/repos/${owner}/${name}`,
            onload: function(response) {
                const repositoryData = JSON.parse(response.responseText);
                const repositorySizeKB = repositoryData.size;
                const repositorySizeMB = (repositorySizeKB / 1024).toFixed(2);

                // Create a button element to display the repository size
                const button = document.createElement('button');
                button.innerHTML = `${repositorySizeMB} MB`;
                button.style.backgroundColor = 'red';
                button.style.color = 'white';
                button.style.border = 'none';
                button.style.padding = '8px 16px';
                button.style.position = 'fixed';
                button.style.top = '100px';
                button.style.right = '10px';
                button.style.zIndex = '9999';

                // Append the button to the document body
                document.body.appendChild(button);
            }
        });
    }

    // Function to check if the current page is a GitHub repository page
    function isRepositoryPage() {
        const pathSegments = window.location.pathname.split('/');
        return (pathSegments.length >= 3 && pathSegments[1] !== '' && pathSegments[2] !== '');
    }

    // Function to get the repository owner and name from the URL
    function getRepositoryInfo() {
        const pathSegments = window.location.pathname.split('/');
        const owner = pathSegments[1];
        const name = pathSegments[2];
        return [owner, name];
    }
})();
