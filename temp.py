for keyword in keywords_array:
    keyword_exists = await objects.execute(Keyword.select(fn.COUNT(Keyword.id)).where(Keyword.keyword.contains(keyword)))

    count = keyword_exists._rows[0][0]

    if count == 0:
        await objects.create(Keyword, keyword=keyword)




	for keyword in keywords_array:
        keyword_exists = Keyword.select().where(Keyword.keyword.contains(keyword)).count()

        if keyword_exists == 0:
            await objects.create(Keyword, keyword=keyword)
