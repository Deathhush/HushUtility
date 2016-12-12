create table files(source_id uniqueidentifier, name nvarchar(max))
--drop table parts
--create table parts(part_id uniqueidentifier, source_id uniqueidentifier, number int, start_time nvarchar(10), end_time nvarchar(10))
--drop table srt_items
create table srt_items(item_id uniqueidentifier, source_id uniqueidentifier, number int, content nvarchar(max), start_time nvarchar(8), end_time nvarchar(8))
--drop table words
create table words(word_id uniqueidentifier, dict_form nvarchar(100), exact_form nvarchar(100), word_count bigint)

create table word_item_mapping(word_id uniqueidentifier, item_id uniqueidentifier)