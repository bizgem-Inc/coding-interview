from inject import Binder


from domain.repository.category import ICategoryRepository
from infrastructure.repository.category import CategoryRepository



def default_config(binder: Binder):
    """
    DI設定
    Interfaceに対応する具象実装クラスを設定します
    """

    binder.bind(ICategoryRepository, CategoryRepository())
