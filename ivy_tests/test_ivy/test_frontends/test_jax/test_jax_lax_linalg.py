# global
import sys
import numpy as np
from hypothesis import strategies as st

# local
import ivy
import ivy_tests.test_ivy.helpers as helpers
from ivy.functional.frontends.jax.lax.linalg import qdwh
from ivy_tests.test_ivy.helpers import assert_all_close
from ivy_tests.test_ivy.helpers import handle_frontend_test


# svd
@handle_frontend_test(
    fn_tree="jax.lax.linalg.svd",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1][0])) != 0
    ),
    full_matrices=st.booleans(),
    compute_uv=st.booleans(),
    test_with_out=st.just(False),
)
def test_jax_lax_svd(
    *,
    dtype_and_x,
    full_matrices,
    compute_uv,
    on_device,
    fn_tree,
    frontend,
    test_flags,
):
    dtype, x = dtype_and_x
    x = np.asarray(x[0], dtype=dtype[0])
    # make symmetric positive-definite beforehand
    x = np.matmul(x.T, x) + np.identity(x.shape[0]) * 1e-3

    ret, frontend_ret = helpers.test_frontend_function(
        input_dtypes=dtype,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        test_values=False,
        x=x,
        full_matrices=full_matrices,
        compute_uv=compute_uv,
    )

    if compute_uv:
        ret = [ivy.to_numpy(x) for x in ret]
        frontend_ret = [np.asarray(x) for x in frontend_ret]

        u, s, vh = ret
        frontend_u, frontend_s, frontend_vh = frontend_ret

        assert_all_close(
            ret_np=u @ np.diag(s) @ vh,
            ret_from_gt_np=frontend_u @ np.diag(frontend_s) @ frontend_vh,
            rtol=1e-2,
            atol=1e-2,
            ground_truth_backend=frontend,
        )
    else:
        assert_all_close(
            ret_np=ivy.to_numpy(ret),
            ret_from_gt_np=np.asarray(frontend_ret[0]),
            rtol=1e-2,
            atol=1e-2,
            ground_truth_backend=frontend,
        )


# cholesky
@handle_frontend_test(
    fn_tree="jax.lax.linalg.cholesky",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1][0])) != 0
    ),
    symmetrize_input=st.booleans(),
    test_with_out=st.just(False),
)
def test_jax_lax_cholesky(
    *,
    dtype_and_x,
    symmetrize_input,
    on_device,
    fn_tree,
    frontend,
    test_flags,
):
    dtype, x = dtype_and_x
    x = np.asarray(x[0], dtype=dtype[0])
    # make symmetric positive-definite beforehand
    x = np.matmul(x.T, x) + np.identity(x.shape[0]) * 1e-3
    helpers.test_frontend_function(
        input_dtypes=dtype,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-02,
        x=x,
        symmetrize_input=symmetrize_input,
    )


# eigh
@handle_frontend_test(
    fn_tree="jax.lax.linalg.eigh",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1][0])) != 0
    ),
    lower=st.booleans(),
    symmetrize_input=st.booleans(),
    test_with_out=st.just(False),
)
def test_jax_lax_eigh(
    *,
    dtype_and_x,
    lower,
    symmetrize_input,
    on_device,
    fn_tree,
    frontend,
    test_flags,
):
    dtype, x = dtype_and_x
    x = np.array(x[0], dtype=dtype[0])
    # make symmetric positive-definite beforehand
    x = np.matmul(x.T, x) + np.identity(x.shape[0]) * 1e-3

    ret, frontend_ret = helpers.test_frontend_function(
        input_dtypes=dtype,
        frontend=frontend,
        test_flags=test_flags,
        fn_tree=fn_tree,
        on_device=on_device,
        test_values=False,
        x=x,
        lower=lower,
        symmetrize_input=symmetrize_input,
    )
    ret = [ivy.to_numpy(x) for x in ret]
    frontend_ret = [np.asarray(x) for x in frontend_ret]

    L, Q = ret
    frontend_Q, frontend_L = frontend_ret

    assert_all_close(
        ret_np=Q @ np.diag(L) @ Q.T,
        ret_from_gt_np=frontend_Q @ np.diag(frontend_L) @ frontend_Q.T,
        atol=1e-2,
    )

@handle_frontend_test(
    fn_tree="jax.lax.linalg.qdwh",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1][0])) != 0
    ),
    is_hermitian=st.booleans(),
    test_with_out=st.just(False),
)
def test_jax_lax_qdwh(
    *,
    x,
    is_hermitian,
    max_iterations,
    eps,
    dynamic_shape,
):
    # Pad x if dynamic_shape is provided
    if dynamic_shape:
        m, n = dynamic_shape
        x_pad = np.zeros((m, n), dtype=x.dtype)
        x_pad[: x.shape[0], : x.shape[1]] = x
        x = x_pad

    # Compute the SVD of x using the reference implementation
    u_ref, s_ref, vh_ref = np.linalg.svd(x, full_matrices=False)
    v_ref = vh_ref.T.conj()

    # Compute the SVD of x using the qdwh function
    u, h, num_iters, is_converged = qdwh(x, is_hermitian=is_hermitian, max_iterations=max_iterations, eps=eps, dynamic_shape=dynamic_shape)
    v = u.conj().T

    # Compute the weighted average of u and v using the reference implementation
    alpha = 0.5
    u_avg_ref = alpha * u_ref + (1 - alpha) * v_ref

    # Compute the diagonal matrix h_ref = u_avg_ref^H * x
    h_ref = u_avg_ref.conj().T @ x

    # Compare u and u_ref
    assert_all_close(u, u_ref, atol=1e-6)

    # Compare h and h_ref
    assert_all_close(h, h_ref, atol=1e-6)

    # Perform additional checks based on the specified conditions
    if is_hermitian:
        # Check if h is Hermitian
        assert_all_close(h, h.conj().T, atol=1e-6)

    if eps:
        # Check convergence based on epsilon
        x_norm = np.linalg.norm(x)
        y = np.linalg.norm(h) * (4 * eps) ** (1 / 3)
        if x_norm < y:
            assert is_converged

    if max_iterations:
        # Check if the maximum number of iterations is reached
        if num_iters >= max_iterations:
            assert not is_converged
