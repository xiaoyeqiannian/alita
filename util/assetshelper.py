#coding: utf-8

'''
改变 assets.debug = True 时返回未压缩静态资源 URL

assets.resolver = BlueprintResolver({
        # folder: (url_prefix, static_folder)
        'simple_page': ('/s', '_static')
    })
'''

import os
import logging
from flask_assets import FlaskResolver


class BlueprintResolver(FlaskResolver):
    def __init__(self, folder_map):
        self.folder_map = folder_map

    def search_for_source(self, ctx, item):
        '''
        '''
        if item.startswith('..'):
            ps = item.split('/')
            folder = ps[1]
            filepath = '/'.join(ps[2:])
            #
            # TODO: 更好的解决方案
            root = os.path.dirname(os.path.dirname(__file__))
            res = '{root}/{folder}/{filepath}'.format(root=root, folder=folder, filepath=filepath)
        else:
            res = super(BlueprintResolver, self).search_for_source(ctx, item)
        logging.debug('search: %s ===> %s', item, res)
        return res

    def split_prefix(self, ctx, item):
        if item.startswith('..'):
            _, folder, static, filepath = item.split('/', 3)
            assert static == 'static'
            # root 得是 {cwd}/shark
            root = os.path.dirname(__file__)
            # 所有文件都输出到了 static
            # res = os.path.join(root, folder), filepath, '{}.cdn'.format(folder)
            res = os.path.join(root, 'static'), filepath, 'static'
        else:
            res = super(BlueprintResolver, self).split_prefix(ctx, item)
        logging.debug('split_prefix: %s ===> %s', item, res)
        return res


    def resolve_source_to_url(self, ctx, filepath, item):
        if item.startswith('..'):
            # print 'ctx._overwrites', ctx._overwrites
            # print 'ctx._parent', ctx._parent._parent
            # print 'filepath', filepath
            # print 'item', item
            '''
            ../{dir}/{static}/
            dir => bp.url_prefix, bp.static_folder
            '''
            ps = item.split('/')
            folder = ps[1]
            filepath = '/'.join(ps[2:])
            res = '{url_prefix}/{filepath}'.format(
                url_prefix=self.folder_map[folder][0], filepath=filepath)
        else:
            res = super(BlueprintResolver, self).resolve_source_to_url(ctx, filepath, item)
        return res
