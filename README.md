Scrapping plan can be defined with SQL-like language...

- Scrape whole page/pages
    ```sql
    SELECT * 
    FROM LOAD('https://example.org') -- load page
    ```
- Scrape specific tags
    ```sql
    SELECT <tag id=... class=...> -- get specific tags only
    FROM LOAD('https://example.org')
    ```
- Scrape from some text file
    ```sql
    SELECT <div class=...>
    FROM (
        SELECT LOAD(_1) -- only for .txt or list-only .yaml files
        -- otherwise: column name for .csv or attr name for .yaml
        FROM READ('/Users/dsp_shp/some-urls.txt') -- read urls from file
    )
    ```
- Scrape with limited pagination
    ```sql
    SELECT * 
    FROM LOAD('https://example.org') 
    LIMIT 10 -- get only first 10 pages
    ```
- Scrape with complex logic and page props defined
    ```sql 
    DECLARE 
        PAGINATION_TAG = <div ...>; -- declared properties
        COOKIE_PATH = '/Users/dsp_shp/some-cookie.COOKIE';

    /*
        Optional comment to fully describe logic here...
        Optional comment to fully describe logic here...
        Optional comment to fully describe logic here...
    */
    SELECT <div id="parent">.<div id="child">, page_spec_info
    FROM (
        SELECT LOAD(<a href="...">.href)
             , <div class='specific_page_info'> as page_spec_info
        FROM LOAD('https://example.org')
        LIMIT 1
    ) _
    ```
