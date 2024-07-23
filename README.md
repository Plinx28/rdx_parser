<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
  <h1>Product Parser</h1>

  <p>This repository contains parsers for gathering information about products from online store.</p>

  <h2>Project Structure:</h2>

  <ul>
    <li><code>async_main.py</code> - Asynchronous parser, which efficiently handles large number of requests.</li>
    <li><code>sync_main.py</code> - Synchronous parser, suitable for smaller volumes of data.</li>
    <li><code>sync_pars_all.py</code> - Full parser that collects information about products and downloads images into a specific file structure.</li>
  </ul>

  <h2>Running Instructions:</h2>

  <p>Run the script you want to use:</p>
    <ul>
      <li><code>python async_main.py</code></li>
      <li><code>python sync_main.py</code></li>
      <li><code>python sync_pars_all.py</code></li>
    </ul>

  <h2>Limitations:</h2>
  
  <p>
    Parsers may have limitations, such as:
    <ul>
      <li>Request rate limits.</li>
      <li>Complex HTML structures that make it difficult to extract data.</li>
      <li>Website changes that may break the parser.</li>
    </ul>
  </p>
</body>
</html>
