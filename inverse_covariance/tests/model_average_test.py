import numpy as np
import pytest

from sklearn import datasets
from sklearn.covariance import GraphLassoCV

from .. import QuicGraphLassoCV, QuicGraphLasso, ModelAverage


class TestQuicGraphLasso(object):
    @pytest.mark.parametrize("params_in", [
        ({
            'estimator': QuicGraphLasso,
            'estimator_args': {},
            'n_trials': 10,
            'normalize': True,
            'subsample': 0.3,
            'penalization': 'random',
        }),
        ({
            'estimator': QuicGraphLasso,
            'estimator_args': {
                'lam': 0.5,
                'mode': 'trace',
            },
            'n_trials': 15,
            'normalize': False,
            'subsample': 0.6,
            'penalization': 'random',
        }),
        ({
            'estimator': QuicGraphLassoCV,
            'estimator_args': {},
            'n_trials': 10,
            'normalize': True,
            'subsample': 0.3,
            'penalization': 'random',
            'use_cache': True,
        }),
        ({
            'estimator': GraphLassoCV,
            'estimator_args': {},
            'n_trials': 10,
            'normalize': True,
            'subsample': 0.3,
            'penalization': 'random',
            'use_cache': True,
            'penalty': 'alpha',
            'use_scalar_penalty': True,
        }),
    ])
    def test_integration_quic_graph_lasso_cv(self, params_in):
        '''
        Just tests inputs/outputs (not validity of result).
        '''
        X = datasets.load_diabetes().data
        ma = ModelAverage(**params_in)
        ma.fit(X)

        n_examples, n_features = X.shape

        assert ma.proportion_.shape == (n_features, n_features)
        if ma.use_cache:
            assert len(ma.estimators_) == ma.n_trials
            assert len(ma.subsets_) == ma.n_trials
            if not ma.use_scalar_penalty:
                assert len(ma.lams_) == ma.n_trials
            else:
                assert len(ma.lams_) == 0
        else:
            assert len(ma.estimators_) == 0
            assert len(ma.lams_) == 0
            assert len(ma.subsets_) == 0

        for e in ma.estimators_:
            assert isinstance(e, params_in['estimator'])
            # sklearn doesnt have this but ours do
            if hasattr(e, 'is_fitted'):
                assert e.is_fitted == True

        if ma.normalize == True:
            assert np.max(ma.proportion_) <= 1.0
        else:        
            assert np.max(ma.proportion_) <= ma.n_trials
                
        assert np.min(ma.proportion_) >= 0.0
        assert np.max(ma.proportion_) > 0.0


