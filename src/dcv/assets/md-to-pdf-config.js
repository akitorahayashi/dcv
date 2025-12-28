module.exports = {
  launch_options: {
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  },
  pdf_options: {
    format: 'a4',
    margin: '30mm 20mm',
    printBackground: true,
    landscape: false,
    scale: 1.0
  },
  css: `  
    body {  
      font-family: 'Noto Sans CJK JP', 'Hiragino Sans', sans-serif;  
      line-height: 1.6;  
      font-size: 11pt;  
    }  
    h1, h2, h3 {  
      page-break-after: avoid;  
    }  
    .page-break {  
      page-break-after: always;  
    }  
  `,
  script: [
    {
      content: `  
        window.MathJax = {  
          tex: {  
            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],  
            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]  
          },  
          startup: {  
            ready: () => {  
              MathJax.startup.defaultReady();  
              MathJax.startup.promise.then(() => {  
                console.log('MathJax initial typesetting complete');  
              });  
            }  
          }  
        };  
      `
    },
    {
      url: "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"
    }
  ]
};
