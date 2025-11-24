package com.defamation.backend.repository;

import com.defamation.backend.domain.ClassificationRequest;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.repository.query.Param;

public interface ClassificationRequestRepository extends JpaRepository<ClassificationRequest, Long> {

    /**
     * 최근 모델 분류 로그 검색/페이징
     * is_deleted = false 만
     */
    @Query("""
        SELECT r FROM ClassificationRequest r
        WHERE r.isDeleted = false
          AND (
            :q IS NULL OR :q = '' OR
            r.problemSituation LIKE %:q%
          )
        ORDER BY r.createdAt DESC
    """)
    Page<ClassificationRequest> search(@Param("q") String q, Pageable pageable);
}
