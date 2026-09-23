顶奢媒体文件命名说明

每个详情页使用一个独立目录，例如：
photos/shanghai-model-001/

照片命名：01.jpg、02.jpg、03.jpg
也支持 jpeg、png、webp、avif 格式；同一编号只保留一种格式。
视频命名：profile.mp4

运行 tools/build_site.py 后，媒体会复制到发布目录；实际存在的图片会自动加入 image-sitemap.xml。
